from prefect import task
import os
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for saving plots
import matplotlib.pyplot as plt
import numpy as np


@task(name="Generate QA Plot", description="Save normalized flat as PNG", tags=["qa", "plot"])
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
