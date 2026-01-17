import os
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for saving plots
import matplotlib.pyplot as plt
import numpy as np
from typing import Optional


def generate_qa_plot(data: np.ndarray, output_path: str, title: str = "Flat QA") -> str:
    """Generate a QA plot for the normalized flat field data."""

    if data is None or not hasattr(data, "shape") or data.ndim != 2:
        raise ValueError(f"Invalid data shape for QA plot: {getattr(data, 'shape', None)}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.figure(figsize=(10, 4))
    fig, ax = plt.subplots()
    im = ax.imshow(data, cmap="gray", aspect="auto", origin="lower")
    fig.colorbar(im, ax=ax)
    plt.title(title)
    plt.savefig(output_path)
    plt.close()
    return output_path


def generate_trace_qa_plot(
    data: np.ndarray,
    left_edges: np.ndarray,
    right_edges: np.ndarray,
    output_path: str,
    title: str = "Slit Trace QA",
    vmin: Optional[float] = None,
    vmax: Optional[float] = None,
) -> str:
    """
    Generate a QA plot showing traced slit edges overlaid on the flat image.

    Args:
        data: 2D flat field image
        left_edges: 2D array of left edge positions (n_slits x n_spectral)
        right_edges: 2D array of right edge positions (n_slits x n_spectral)
        output_path: Path to save the plot
        title: Plot title
        vmin: Minimum value for image scaling
        vmax: Maximum value for image scaling

    Returns:
        Path to saved plot
    """
    if data is None or not hasattr(data, "shape") or data.ndim != 2:
        raise ValueError(f"Invalid data shape for QA plot: {getattr(data, 'shape', None)}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 8))

    # Display the flat image
    if vmin is None:
        vmin = np.percentile(data, 1)
    if vmax is None:
        vmax = np.percentile(data, 99)

    im = ax.imshow(data, cmap="gray", aspect="auto", origin="lower", vmin=vmin, vmax=vmax)
    fig.colorbar(im, ax=ax, label="Counts")

    # Overlay traced edges
    n_slits = left_edges.shape[0] if left_edges.size > 0 else 0
    nspec = data.shape[0]
    spectral_coords = np.arange(nspec)

    colors = plt.cm.tab10(np.linspace(0, 1, max(n_slits, 1)))

    for i in range(n_slits):
        color = colors[i % len(colors)]
        # Plot left edge
        ax.plot(left_edges[i], spectral_coords, color=color, linewidth=1.5, label=f"Slit {i+1}" if i < 10 else None)
        # Plot right edge
        ax.plot(right_edges[i], spectral_coords, color=color, linewidth=1.5, linestyle="--")

    ax.set_xlabel("Spatial (pixels)")
    ax.set_ylabel("Spectral (pixels)")
    ax.set_title(f"{title} - {n_slits} slits detected")

    if n_slits > 0 and n_slits <= 10:
        ax.legend(loc="upper right", fontsize=8)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()

    return output_path
