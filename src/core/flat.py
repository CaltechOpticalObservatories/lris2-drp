import os
import numpy as np
from astropy.io import fits
from typing import Tuple, List, Optional
from scipy.interpolate import splrep, BSpline
from .tracing import trace_slits_1d


def load_flat_frame(filepath: str) -> Tuple[np.ndarray, dict]:
    """Load a FITS file and return its data and header."""
    with fits.open(filepath) as hdul:
        data = hdul[0].data.astype(np.float64)
        header = hdul[0].header
    return data, header


def normalize_flat(data: np.ndarray) -> np.ndarray:
    """
    Normalize the flat field data by dividing by the median of the illuminated area.
    """
    data = data.astype(np.float64)

    # Define illuminated area as pixels above 10% of maximum value
    threshold = 0.1 * np.max(data)
    illuminated_mask = data > threshold

    # Compute median from illuminated area only
    if np.any(illuminated_mask):
        median = np.median(data[illuminated_mask])
    else:
        # Fallback: use median of all positive values
        median = np.median(data[data > 0])

    # Normalize - result should be ~1.0 in illuminated areas
    return data / median


def create_flat_correction(norm_data: np.ndarray) -> np.ndarray:
    """Create a flat correction map by inverting the normalized flat."""
    correction = 1.0 / (norm_data + 1e-8)  # Avoid division by zero
    correction[np.isnan(correction)] = 1.0
    correction[np.isinf(correction)] = 1.0
    return correction


def save_correction_fits(correction: np.ndarray, header: dict, output_path: str) -> str:
    """Save the flat field correction map to a FITS file.

    The correction map contains multiplicative factors (~1.0) to apply to science frames:
        corrected_science = raw_science * correction
    """
    # Add DRP history to header
    header.add_history("DRP: Flat field correction map created")
    header["FLATCORR"] = (True, "Flat field correction map")

    hdu = fits.PrimaryHDU(data=correction, header=header)
    hdul = fits.HDUList([hdu])
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    hdul.writeto(output_path, overwrite=True)
    return output_path


def fit_bspline_1d(x: np.ndarray, y: np.ndarray, n_knots: int = 100, k: int = 3) -> Tuple[np.ndarray, np.ndarray]:
    """
    Fit a B-spline to 1D data and return the fit.

    Simplified version of Bspline.iterfit

    Args:
        x: x-coordinates (must be sorted)
        y: y-values
        n_knots: Number of internal knots for the spline
        k: Spline order (3 = cubic)

    Returns:
        Tuple of (fitted_y, knots_used)
    """
    # Remove NaN and inf values
    valid = np.isfinite(x) & np.isfinite(y)
    x_valid = x[valid]
    y_valid = y[valid]

    if len(x_valid) < k + 1:
        # Not enough points for spline, return mean
        return np.full_like(y, np.mean(y_valid)), np.array([])

    # Create knots evenly spaced across the data range
    x_min, x_max = np.min(x_valid), np.max(x_valid)
    # Adjust n_knots if we don't have enough data points
    n_knots = min(n_knots, len(x_valid) // (k + 1))
    if n_knots < 1:
        n_knots = 1

    knots = np.linspace(x_min, x_max, n_knots + 2)[1:-1]

    # Fit the spline
    try:
        tck = splrep(x_valid, y_valid, t=knots, k=k, s=0)
        fitted = BSpline(*tck)(x)
    except Exception:
        # Fallback to polynomial fit if spline fails
        coeffs = np.polyfit(x_valid, y_valid, min(3, len(x_valid) - 1))
        fitted = np.polyval(coeffs, x)
        knots = np.array([])

    return fitted, knots


def normalize_flat_spectroscopic(
    data: np.ndarray,
    slit_positions: Optional[List[int]] = None,
    slit_width: int = 50,
    n_knots_spectral: int = 100,
    low_signal_threshold: float = 30.0,
    edge_trim_pixels: int = 5
) -> np.ndarray:
    """
    Spectroscopic flat normalization using B-spline fitting.
    (simplified from KCWI)

    1. Identifies slit traces
    2. For each slit, fits a smooth B-spline along the spectral direction
    3. Creates a smooth model of the illumination pattern
    4. Normalizes the flat to create a ratio map

    Args:
        data: 2D flat field image (spatial x spectral)
        slit_positions: Optional list of slit center positions. If None, auto-detect.
        slit_width: Width around each slit center to extract (pixels)
        n_knots_spectral: Number of knots for B-spline fit along spectral direction
        low_signal_threshold: Pixels below this value get no correction
        edge_trim_pixels: Number of pixels to trim from edges of each slit

    Returns:
        Normalized flat field (ratio map for correction)
    """
    data = data.astype(np.float64)
    ny, nx = data.shape

    # Auto-detect slits if not provided
    if slit_positions is None:
        slit_positions = trace_slits_1d(data)

    if len(slit_positions) == 0:
        # Fallback to simple normalization if no slits found
        print("Warning: No slits detected, using simple normalization")
        return normalize_flat(data)

    print(f"Processing {len(slit_positions)} slits")

    # Create smooth model of the flat field
    flat_model = np.zeros_like(data)

    # Process each slit
    for slit_idx, slit_center in enumerate(slit_positions):
        # Define slit region
        y_start = max(0, slit_center - slit_width // 2)
        y_end = min(ny, slit_center + slit_width // 2)

        # Extract slit region
        slit_data = data[y_start:y_end, :]

        # For each column (spectral pixel), get median across slit
        spectral_profile = np.median(slit_data, axis=0)

        # Fit B-spline along spectral direction
        x_coords = np.arange(nx)
        spectral_fit, _ = fit_bspline_1d(x_coords, spectral_profile, n_knots=n_knots_spectral)

        # Replicate the fit across the slit width
        for i in range(y_start, y_end):
            # Apply edge trimming
            if i < y_start + edge_trim_pixels or i >= y_end - edge_trim_pixels:
                flat_model[i, :] = 0.0  # Will be masked later
            else:
                flat_model[i, :] = spectral_fit

    # Create ratio map
    ratio = np.ones_like(data)

    # Only correct where we have valid model and good signal
    valid = (flat_model > 0) & (data > low_signal_threshold)
    ratio[valid] = flat_model[valid] / data[valid]

    # Trim unreasonable values
    ratio[ratio < 0] = 1.0  # Negative ratios (line 906-908)
    ratio[ratio > 3.0] = 1.0  # High ratios at edges (line 911-915)
    ratio[~np.isfinite(ratio)] = 1.0  # NaN/inf values

    # Low signal regions get no correction
    ratio[data < low_signal_threshold] = 1.0

    return ratio


def create_master_flat(flat_data: np.ndarray, **kwargs) -> np.ndarray:
    """
    Create a master flat correction map.

    Args:
        flat_data: 2D flat field image
        **kwargs: Additional arguments

    Returns:
        Master flat correction map (multiply science data by this)
    """
    ratio = normalize_flat_spectroscopic(flat_data, **kwargs)
    # The ratio is already the correction map
    correction = ratio
    
    return correction
