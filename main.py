# main.py
import os
if "PREFECT_API_URL" in os.environ:
    del os.environ["PREFECT_API_URL"]
import yaml
from lris2_drp.flows import batch_process_all_flats

def load_config(config_path="config.yaml"):
    """Load configuration from a YAML file."""
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

if __name__ == "__main__":
    config = load_config()
    batch_process_all_flats(
        input_dir=config["input_dir"],
        output_dir=config["output_dir"]
    )
