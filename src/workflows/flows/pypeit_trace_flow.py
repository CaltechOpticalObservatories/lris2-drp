"""
PyPEIT-based slit tracing flow.
"""
import os
from prefect import flow, task, get_run_logger
from prefect.task_runners import ConcurrentTaskRunner
from workflows.prefect_tasks.save_trace import save_trace_solution_task
from workflows.prefect_tasks.pypeit_tasks import (
    load_flat_frame_task,
    trace_slits_pypeit_task,
    get_slit_centers_task,
    save_edge_trace_task,
    generate_trace_qa_plot_task,
)


@task(name="Trace Slits (PyPEIT)")
def trace_slits_pypeit(fits_path: str, output_dir: str):
    """
    Trace slits in a FITS file using PyPEIT algorithms.

    Args:
        fits_path: Path to input FITS file
        output_dir: Output directory for results
    """
    logger = get_run_logger()
    filename = os.path.splitext(os.path.basename(fits_path))[0]

    # Construct output paths
    trace_output = os.path.join(output_dir, filename, "slit_trace.txt")
    edges_output = os.path.join(output_dir, filename, "slit_edges.npz")
    qa_output = os.path.join(output_dir, filename, "trace_qa.png")

    # Ensure output dirs
    os.makedirs(os.path.dirname(trace_output), exist_ok=True)

    # Load FITS
    logger.info(f"Loading {fits_path}")
    data, header = load_flat_frame_task(fits_path)

    # Trace slits with PyPEIT
    logger.info("Tracing slits with PyPEIT EdgeTraceSet")
    left_edges, right_edges = trace_slits_pypeit_task(data)

    # Get slit centers for compatibility with existing outputs
    slit_positions = get_slit_centers_task(left_edges, right_edges)
    logger.info(f"Found {len(slit_positions)} slits")

    # Save outputs
    logger.info("Saving results")
    save_trace_solution_task(slit_positions, trace_output)
    save_edge_trace_task(left_edges, right_edges, edges_output)

    # Generate QA plot
    logger.info("Generating QA plot")
    generate_trace_qa_plot_task(data, left_edges, right_edges, qa_output, title=filename)

    logger.info(f"Finished tracing {fits_path}")


@flow(
    name="PyPEIT Slit Tracing",
    description="Trace slits in FITS frames using PyPEIT algorithms",
    task_runner=ConcurrentTaskRunner(max_workers=2),
)
def pypeit_trace_flow(input_dir: str, output_dir: str):
    """
    Trace slits in all FITS files using PyPEIT algorithms.

    This flow uses PyPEIT's EdgeTraceSet for slit tracing.

    Args:
        input_dir: Directory containing input FITS files
        output_dir: Directory for output files
    """
    logger = get_run_logger()

    fits_files = [
        os.path.join(input_dir, f)
        for f in os.listdir(input_dir)
        if f.lower().endswith(".fits")
    ]
    logger.info(f"Found {len(fits_files)} FITS files in {input_dir}")

    futures = [
        trace_slits_pypeit.submit(fp, output_dir)
        for fp in fits_files
    ]

    for future in futures:
        future.result()

    logger.info("PyPEIT slit tracing complete")
