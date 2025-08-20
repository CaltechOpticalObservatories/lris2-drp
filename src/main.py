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
    input_dir = config["input_dir"]
    output_dir = config["output_dir"]

    os.makedirs(output_dir, exist_ok=True)

    print(f"🟢 Starting batch processing of FITS files in {input_dir}")
    batch_process_all_flats(input_dir=input_dir, output_dir=output_dir)
