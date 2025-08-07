"""
Main entry point for the LRIS2 Data Reduction Pipeline (DRP).
This script initializes the pipeline and processes all flat field FITS files
found in the specified input directory, saving the results to the output directory.
"""
import yaml
import os
from workflows.flows.batch_flat_flow import batch_process_all_flats

def load_config(config_path="config/config.yaml"):
    """Load configuration from a YAML file."""
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

if __name__ == "__main__":
    config = load_config()
    input_dir = config['input_dir']
    output_dir = config['output_dir']
    
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if not filename.lower().endswith(".fits"):
            continue

        flat_fits_path = os.path.join(input_dir, filename)
        base_name = os.path.splitext(filename)[0]
        file_out_dir = os.path.join(output_dir, base_name)
        os.makedirs(file_out_dir, exist_ok=True)

        corrected_output = os.path.join(file_out_dir, "flat_corrected.fits")
        trace_output = os.path.join(file_out_dir, "slit_trace.txt")
        qa_output = os.path.join(file_out_dir, "flat_qa.png")

        print(f"🟢 Processing {flat_fits_path}")
        batch_process_all_flats(
            flat_fits_path=flat_fits_path,
            corrected_output=corrected_output,
            trace_output=trace_output,
            qa_output=qa_output
        )
