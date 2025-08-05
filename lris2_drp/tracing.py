from prefect import task
from typing import List
import os
import numpy as np
from scipy.signal import find_peaks

@task(name="Trace Slits", description="Find slit center peaks by collapsing along dispersion axis", tags=["trace"])
def trace_slits_1d(data: np.ndarray) -> List[int]:
    """Trace slit positions by finding peaks in the 1D profile of the flat field data."""
    profile = np.median(data, axis=1)
    peaks, _ = find_peaks(profile, distance=20, prominence=0.05)
    return list(peaks)


@task(name="Save Trace Solution", description="Write slit positions to file", tags=["save", "trace"])
def save_trace_solution(slit_positions: List[int], output_path: str) -> str:
    """Save the traced slit positions to a text file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        for pos in slit_positions:
            f.write(f"{pos}\n")
    return output_path
