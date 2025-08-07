import os
from prefect import flow
from workflows.prefect_tasks.load_flat import load_flat_frame_task
from workflows.prefect_tasks.normalize_flat import normalize_flat_task
from workflows.prefect_tasks.create_correction import create_flat_correction_task
from workflows.prefect_tasks.trace_slits import trace_slits_task
from workflows.prefect_tasks.save_corrected import save_corrected_fits_task
from workflows.prefect_tasks.save_trace import save_trace_solution_task
from workflows.prefect_tasks.qa_plot import generate_qa_plot_task

@flow(name="LRIS2 Flat Pipeline")
def batch_process_all_flats(flat_fits_path: str, corrected_output: str, trace_output: str, qa_output: str):
    """Batch process a single LRIS2 flat FITS file through all DRP steps."""
    
    # Ensure output directories exist
    os.makedirs(os.path.dirname(corrected_output), exist_ok=True)
    os.makedirs(os.path.dirname(trace_output), exist_ok=True)
    os.makedirs(os.path.dirname(qa_output), exist_ok=True)
    
    # Load FITS
    data, header = load_flat_frame_task(flat_fits_path)

    # Normalize flat
    norm = normalize_flat_task(data)

    # Create correction
    correction = create_flat_correction_task(norm)

    # Trace slits
    slit_positions = trace_slits_task(data)

    # Save outputs
    save_corrected_fits_task(data, correction, header, corrected_output)
    save_trace_solution_task(slit_positions, trace_output)
    generate_qa_plot_task(norm, qa_output)