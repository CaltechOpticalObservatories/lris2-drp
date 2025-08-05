from prefect import flow, task, get_run_logger
from prefect.task_runners import ConcurrentTaskRunner
import os
from lris2_drp.flat import (
    load_flat_frame,
    normalize_flat,
    create_flat_correction,
    save_corrected_fits,
)
from lris2_drp.tracing import trace_slits_1d, save_trace_solution
from lris2_drp.qa import generate_qa_plot

@task(name="Process Single LRIS2 Flat Frame", description="Run all DRP steps on a single flat FITS file")
def process_flat_frame(filepath: str, output_dir: str):
    """Process a single LRIS2 flat field FITS file through all DRP steps."""
    filename = os.path.splitext(os.path.basename(filepath))[0]

    data, header = load_flat_frame(filepath)
    norm = normalize_flat(data)
    correction = create_flat_correction(norm)
    slit_positions = trace_slits_1d(data)

    trace_path = os.path.join(output_dir, filename, "slit_trace.txt")
    plot_path = os.path.join(output_dir, filename, "flat_norm_qa.png")
    corrected_path = os.path.join(output_dir, filename, "flat_corrected.fits")

    save_trace_solution(slit_positions, trace_path)
    generate_qa_plot(norm, plot_path, title=f"Normalized Flat: {filename}")
    save_corrected_fits(data, correction, header, corrected_path)


@flow(
    name="Batch Process LRIS2 Flats",
    description="Batch process all LRIS2 flats in parallel",
    task_runner=ConcurrentTaskRunner(max_workers=2),  # Adjust concurrency here
)
def batch_process_all_flats(input_dir: str, output_dir: str):
    """Batch process all LRIS2 flat field FITS files in the input directory."""
    logger = get_run_logger()

    fits_files = [
        os.path.join(input_dir, f)
        for f in os.listdir(input_dir)
        if f.lower().endswith(".fits")
    ]

    logger.info(f"Found {len(fits_files)} FITS files.")

    futures = [process_flat_frame.submit(fp, output_dir) for fp in fits_files]

    # Wait for all to complete
    for future in futures:
        future.result()
