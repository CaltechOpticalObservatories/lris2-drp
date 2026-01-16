"""
PyPEIT-based slit tracing.
"""
import os
from typing import Tuple, List, Optional
import numpy as np

from pypeit.images.buildimage import TraceImage
from pypeit.edgetrace import EdgeTraceSet
from pypeit.par.pypeitpar import EdgeTracePar
from pypeit.spectrographs.util import load_spectrograph


def trace_slits_pypeit(
    data: np.ndarray,
    spectrograph_name: str = 'keck_lris_red',
    fwhm_uniform: float = 3.0,
    niter_uniform: int = 9,
    det_min_spec_length: float = 0.3,
    follow_span: int = 20,
    fit_order: int = 5,
) -> Tuple[np.ndarray, np.ndarray, Optional[object]]:
    """
    Trace slit edges using PyPEIT's EdgeTraceSet.

    Args:
        data: 2D flat field image (spatial x spectral)
        spectrograph_name: PyPEIT spectrograph name (default: keck_lris_red)
            Use keck_lris_red or keck_lris_blue as proxy for LRIS2 evaluation
        fwhm_uniform: FWHM for uniform filter smoothing
        niter_uniform: Number of iterations for uniform filter
        det_min_spec_length: Minimum spectral length for valid trace (fraction)
        follow_span: Number of pixels to use when following edges
        fit_order: Polynomial order for trace fitting

    Returns:
        Tuple of:
            - left_edges: 2D array of left edge positions (n_slits x n_spectral)
            - right_edges: 2D array of right edge positions (n_slits x n_spectral)
            - edges: The EdgeTraceSet object (for advanced use/saving)
    """
    # Load spectrograph (required by PyPEIT)
    spectrograph = load_spectrograph(spectrograph_name)

    # Build EdgeTracePar with our settings
    edge_par = EdgeTracePar()
    edge_par['fwhm_uniform'] = fwhm_uniform
    edge_par['niter_uniform'] = niter_uniform
    edge_par['det_min_spec_length'] = det_min_spec_length
    edge_par['follow_span'] = follow_span
    edge_par['fit_order'] = fit_order

    # Create TraceImage from numpy array
    # PyPEIT expects the image in a specific format
    trace_img = TraceImage(data.astype(np.float64))

    # Create EdgeTraceSet with spectrograph for proper defaults
    # Use auto=True to run the full tracing pipeline automatically
    # This handles PCA decomposition, edge syncing, and all refinement steps
    edges = EdgeTraceSet(
        trace_img,
        spectrograph=spectrograph,
        par=edge_par,
        auto=True,  # Run full pipeline automatically
    )

    # Extract edge positions
    # edges.edge_fit contains the fitted edge positions
    # Shape is (nspec, ntrace) where ntrace = 2 * nslits
    if edges.edge_fit is None or edges.edge_fit.size == 0:
        # No edges found - return empty arrays
        nspec = data.shape[0]
        return np.array([]).reshape(0, nspec), np.array([]).reshape(0, nspec), edges

    # Separate left and right edges
    # In PyPEIT, left edges have negative trace IDs, right have positive
    left_mask = edges.traceid < 0
    right_mask = edges.traceid > 0

    # Get edge positions (shape: nspec x ntrace)
    edge_positions = edges.edge_fit

    # Extract left and right edges
    left_edges = edge_positions[:, left_mask].T  # (n_slits, nspec)
    right_edges = edge_positions[:, right_mask].T  # (n_slits, nspec)

    return left_edges, right_edges, edges


def get_slit_centers(left_edges: np.ndarray, right_edges: np.ndarray) -> List[int]:
    """
    Calculate slit center positions from left/right edges.

    This provides compatibility with the existing trace_slits_1d interface.

    Args:
        left_edges: 2D array of left edge positions (n_slits x n_spectral)
        right_edges: 2D array of right edge positions (n_slits x n_spectral)

    Returns:
        List of slit center positions (median across spectral direction)
    """
    if left_edges.size == 0 or right_edges.size == 0:
        return []

    # Calculate center as midpoint between left and right edges
    # Use median along spectral direction for single position per slit
    centers = (np.median(left_edges, axis=1) + np.median(right_edges, axis=1)) / 2
    return [int(c) for c in centers]


def save_edge_trace(
    left_edges: np.ndarray,
    right_edges: np.ndarray,
    output_path: str
) -> str:
    """
    Save slit edge traces to a numpy file.

    Args:
        left_edges: 2D array of left edge positions
        right_edges: 2D array of right edge positions
        output_path: Path for output file

    Returns:
        Path to saved file
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    np.savez(
        output_path,
        left_edges=left_edges,
        right_edges=right_edges
    )
    return output_path
