"""
Prefect task wrappers for PyPEIT-based processing.
"""
from typing import Tuple, List
import numpy as np
from prefect import task, get_run_logger

from core.flat import load_flat_frame
from core.pypeit_tracing import trace_slits_pypeit, get_slit_centers, save_edge_trace
from core.qa import generate_trace_qa_plot
from core.pypeit_wavesol import make_wavecalib_pypeit


@task(name="Trace Slits PyPEIT")
def trace_slits_pypeit_task(
    data: np.ndarray,
    **kwargs
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Prefect task to trace slits using PyPEIT's EdgeTraceSet.

    Args:
        data: 2D flat field image
        **kwargs: Additional arguments for trace_slits_pypeit

    Returns:
        Tuple of (left_edges, right_edges)
    """
    logger = get_run_logger()
    logger.info("Running PyPEIT edge tracing")

    left_edges, right_edges, edges = trace_slits_pypeit(data, **kwargs)

    n_slits = left_edges.shape[0] if left_edges.size > 0 else 0
    logger.info(f"PyPEIT found {n_slits} slits")

    return left_edges, right_edges, edges


@task(name="Get Slit Centers PyPEIT")
def get_slit_centers_task(
    left_edges: np.ndarray,
    right_edges: np.ndarray
) -> List[int]:
    """
    Prefect task to get slit center positions from edge arrays.

    Args:
        left_edges: 2D array of left edge positions
        right_edges: 2D array of right edge positions

    Returns:
        List of slit center positions
    """
    return get_slit_centers(left_edges, right_edges)


@task(name="Save Edge Trace")
def save_edge_trace_task(
    left_edges: np.ndarray,
    right_edges: np.ndarray,
    output_path: str
) -> str:
    """
    Prefect task to save edge trace arrays.

    Args:
        left_edges: 2D array of left edge positions
        right_edges: 2D array of right edge positions
        output_path: Path for output file

    Returns:
        Path to saved file
    """
    logger = get_run_logger()
    logger.info(f"Saving edge traces to {output_path}")
    return save_edge_trace(left_edges, right_edges, output_path)


@task(name="Load Flat Frame")
def load_flat_frame_task(filepath: str) -> Tuple[np.ndarray, dict]:
    """
    Prefect task to load a FITS file.

    Args:
        filepath: Path to FITS file

    Returns:
        Tuple of (data, header)
    """
    logger = get_run_logger()
    logger.info(f"Loading FITS file: {filepath}")
    return load_flat_frame(filepath)


@task(name="Generate Trace QA Plot")
def generate_trace_qa_plot_task(
    data: np.ndarray,
    left_edges: np.ndarray,
    right_edges: np.ndarray,
    output_path: str,
    title: str = "Slit Trace QA",
) -> str:
    """
    Prefect task to generate a QA plot for traced slits.

    Args:
        data: 2D flat field image
        left_edges: 2D array of left edge positions
        right_edges: 2D array of right edge positions
        output_path: Path to save the plot
        title: Plot title

    Returns:
        Path to saved plot
    """
    logger = get_run_logger()
    logger.info(f"Generating trace QA plot: {output_path}")
    return generate_trace_qa_plot(data, left_edges, right_edges, output_path, title)


@task(name="Generate wave calib")
def make_wavecalib_pypeit_task(
        data: np.ndarray,
        slits,
        **kwargs
):
    logger = get_run_logger()
    logger.info(f"Generating wave calib")
    return make_wavecalib_pypeit(data, slits, **kwargs)