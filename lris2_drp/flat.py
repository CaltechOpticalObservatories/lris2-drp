import os
from prefect import task
import numpy as np
from astropy.io import fits
from typing import Tuple

@task(name="Load FITS Frame", description="Load a flat field FITS file", tags=["load"])
def load_flat_frame(filepath: str) -> Tuple[np.ndarray, dict]:
    """Load a FITS file and return its data and header."""
    with fits.open(filepath) as hdul:
        data = hdul[0].data
        header = hdul[0].header
    return data, header


@task(name="Normalize Flat", description="Normalize the flat field by median", tags=["normalize"])
def normalize_flat(data: np.ndarray) -> np.ndarray:
    """Normalize the flat field data by dividing by the median value."""
    median = np.median(data[data > 0])
    return data / median


@task(name="Create Flat Correction", description="Invert normalized flat to create correction map", tags=["correction"])
def create_flat_correction(norm_data: np.ndarray) -> np.ndarray:
    """Create a flat correction map by inverting the normalized flat."""
    correction = 1.0 / (norm_data + 1e-8) # Avoid division by zero
    correction[np.isnan(correction)] = 1.0
    correction[np.isinf(correction)] = 1.0
    return correction


@task(name="Save Corrected FITS", description="Apply flat correction and write corrected FITS file", tags=["output", "fits"])
def save_corrected_fits(original_data: np.ndarray, correction: np.ndarray, header: dict, output_path: str) -> str:
    """Apply the flat correction to the original data and save as a new FITS file."""
    corrected_data = original_data * correction

    # Add DRP history to header
    header.add_history("DRP: Flat field correction applied")
    header["FLATCORR"] = (True, "Flat field correction applied")

    hdu = fits.PrimaryHDU(data=corrected_data, header=header)
    hdul = fits.HDUList([hdu])
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    hdul.writeto(output_path, overwrite=True)
    return output_path
