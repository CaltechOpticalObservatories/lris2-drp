"""
Main entry point for the LRIS2 Data Reduction Pipeline (DRP).
This script initializes the pipeline and processes all flat field FITS files
found in the specified input directory, saving the results to the output directory.
"""
import yaml
import os
import subprocess
from workflows.flows.batch_flat_flow import batch_process_all_flats
from workflows.flows.pypeit_trace_flow import pypeit_trace_flow
from workflows.flows.pypeit_wavesol_flow import pypeit_wavesol_flow

def load_config(config_path="config/config.yaml"):
    """Load configuration from a YAML file."""
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

if __name__ == "__main__":
    config = load_config()
    input_dir_flats = config["input_dir_flats"]
    input_dir_arcs = config["input_dir_arcs"]
    output_dir = config["output_dir"]
    use_prefect_server = config.get("use_prefect_server", True)

    os.makedirs(output_dir, exist_ok=True)

    server_process = None
    if use_prefect_server:
        print("🚀 Starting Prefect server with UI...")
        # Start Prefect server in background
        server_process = subprocess.Popen(
            ["prefect", "server", "start"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        print("✅ Prefect server started!")
        print("🌐 Dashboard available at: http://127.0.0.1:4200")
        print()

    try:
        print(f"🟢 Starting batch processing of FITS files in {input_dir_flats}")
        # batch_process_all_flats(input_dir=input_dir, output_dir=output_dir)
        # pypeit_trace_flow(input_dir=input_dir_flats, output_dir=output_dir)
        print(f"🟢 Starting batch processing of FITS files in {input_dir_arcs}")
        pypeit_wavesol_flow(input_dir=input_dir_arcs, output_dir=output_dir)

        if use_prefect_server:
            print("\n✅ Pipeline completed!")
            print("🌐 View the dashboard at: http://127.0.0.1:4200")
            print("📊 Press Ctrl+C to stop the server and exit.\n")
            
            try:
                # Keep running so server stays up
                import signal
                signal.pause()
                
            except KeyboardInterrupt:
                print("\n🛑 Received interrupt signal...")
                raise
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    finally:
        if server_process:
            print("Stopping Prefect server...")
            server_process.terminate()
            server_process.wait()
            print("Server stopped.")
