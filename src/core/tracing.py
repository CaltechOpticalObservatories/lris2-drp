from typing import List
import os
import numpy as np
from scipy.signal import find_peaks, medfilt


def trace_slits_1d(data: np.ndarray) -> List[int]:
    """Trace slit positions by finding peaks in the 1D profile of the flat field data."""
    profile = np.median(data, axis=0)
    neg_profile = np.zeros(len(profile)+2)
    neg_profile[1:-1] = -1*medfilt(profile, kernel_size=15)
    neg_profile[[0,len(neg_profile)-1]] = np.min(neg_profile)
    edges, _ = find_peaks(neg_profile, distance=40, prominence=0.05)
    # Identify slit centers as midpoints between edges
    centers = (edges[0:-1] + edges[1:]) // 2
    return centers.tolist()


def save_trace_solution(slit_positions: List[int], output_path: str) -> str:
    """Save the traced slit positions to a text file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        for pos in slit_positions:
            f.write(f"{pos}\n")
    return output_path
