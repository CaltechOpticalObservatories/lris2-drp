import os
from prefect import flow, task, get_run_logger
from prefect.task_runners import ConcurrentTaskRunner
from workflows.prefect_tasks.load_flat import load_flat_frame_task
from workflows.prefect_tasks.normalize_flat import normalize_flat_task
from workflows.prefect_tasks.create_correction import create_flat_correction_task
from workflows.prefect_tasks.trace_slits import trace_slits_task
from workflows.prefect_tasks.save_corrected import save_corrected_fits_task
from workflows.prefect_tasks.save_trace import save_trace_solution_task
from workflows.prefect_tasks.qa_plot import generate_qa_plot_task


@task(name="Process Single Flat Frame")
def process_single_flat_frame(flat_fits_path: str, output_dir: str):
    """Process a single LRIS2 flat FITS file through all DRP steps."""
    logger = get_run_logger()
    filename = os.path.splitext(os.path.basename(flat_fits_path))[0]

    # Construct output paths
    corrected_output = os.path.join(output_dir, filename, "flat_corrected.fits")
    trace_output = os.path.join(output_dir, filename, "slit_trace.txt")
    qa_output = os.path.join(output_dir, filename, "flat_norm_qa.png")

    # Ensure output dirs
    os.makedirs(os.path.dirname(corrected_output), exist_ok=True)

    # Load FITS
    data, header = load_flat_frame_task(flat_fits_path)

    # DRP steps
    norm = normalize_flat_task(data)
    correction = create_flat_correction_task(norm)
    slit_positions = trace_slits_task(data)

    # Save outputs
    save_corrected_fits_task(data, correction, header, corrected_output)
    save_trace_solution_task(slit_positions, trace_output)
    generate_qa_plot_task(norm, qa_output)

    logger.info(f"Finished processing {flat_fits_path}")

@flow(
    name="Batch Process LRIS2 Flats",
    description="Process all flat frames concurrently using Prefect",
    task_runner=ConcurrentTaskRunner(max_workers=2),  # You can adjust this
)
def batch_process_all_flats(input_dir: str, output_dir: str):
    """Process all FITS files in a directory using concurrent subflows."""
    logger = get_run_logger()

    fits_files = [
        os.path.join(input_dir, f)
        for f in os.listdir(input_dir)
        if f.lower().endswith(".fits")
    ]
    logger.info(f"Found {len(fits_files)} FITS files in {input_dir}.")

    futures = [process_single_flat_frame.submit(fp, output_dir) for fp in fits_files]

    for future in futures:
        future.result()
