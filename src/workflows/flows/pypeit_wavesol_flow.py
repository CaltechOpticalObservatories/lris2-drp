import os, glob
import numpy as np

from pypeit import edgetrace

from prefect import flow, task, get_run_logger
from prefect.task_runners import ConcurrentTaskRunner
from workflows.prefect_tasks.save_trace import save_trace_solution_task
from workflows.prefect_tasks.pypeit_tasks import (
    load_flat_frame_task,
    make_wavecalib_pypeit_task
)

@task(name="Wave calib (Pypeit)")
def make_wavecalib_pypeit(arc_filenames, edges_file, output_dir):
    logger = get_run_logger()

    # Get detector (red/blue) from first filename
    detector = "Red" if "Red" in arc_filenames[0] else "Blue"
    logger.info(f"Combining all {len(arc_filenames)} {detector} lamps in one FITS frame")
    stacked_data, lampnums = [], []
    for filename in arc_filenames:
        logger.info(f"Loading {filename}")
        data, header = load_flat_frame_task(filename)
        stacked_data.append(data)
        lampnums.append(filename.split("Lamp")[1][0])  # Extract lamp number
    data = np.sum(stacked_data, axis=0)

    # construct output paths
    wv_calib_output = os.path.join(output_dir, f"{detector}_wv_calib.fits")
    diag_output = os.path.join(output_dir, f"{detector}_wavesol_diagnostic.csv")

    # Ensure output dirs
    os.makedirs(output_dir, exist_ok=True)

    # load trace slits
    slits = edgetrace.EdgeTraceSet.from_file(edges_file).get_slits()

    # get arc lamp
    lampdict = {"1": "HgI", "2": "NeI", "3": "ArI", "4": "ZnI", "5": "CdI"}
    lamps = [lampdict[num] for num in lampnums]
    spec_name = "keck_lris_red" if detector == "Red" else "keck_lris_blue"

    # set method
    method = "holy-grail"

    # call prefect task to make wavecalib
    wv_calib = make_wavecalib_pypeit_task(data, slits, lamps=lamps, spectrograph_name=spec_name, method=method)

    # Save wavecalib and diagnostics
    wv_calib.to_file(wv_calib_output)
    diag = wv_calib.wave_diagnostics(print_diag=True)
    diag.write(diag_output, format="csv")
    return wv_calib

@flow(name="Wave calib (Pypeit)", task_runner=ConcurrentTaskRunner(max_workers=2))
def pypeit_wavesol_flow(input_dir, output_dir):
    logger = get_run_logger()

    blue_arcs = sorted(glob.glob(os.path.join(input_dir, "*Blue*Lamp*")))
    red_arcs = sorted(glob.glob(os.path.join(input_dir, "*Red*Lamp*")))
    logger.info(f"Found {len(blue_arcs)} Blue arc files, and {len(red_arcs)} Red arc files in {input_dir}")


    # Load edges file from output_dir
    red_edges = glob.glob(os.path.join(output_dir, "*Red*/edges.fits"))
    blue_edges = glob.glob(os.path.join(output_dir, "*Blue*/edges.fits"))
    print(f"Found {len(red_edges)} red edges in {output_dir}")
    print(f"Found {len(blue_edges)} blue edges in {output_dir}")
    if not red_edges and not blue_edges:
        raise RuntimeError(f"No edge files found in {output_dir}. Please run the tracing flow first.")
    red_edges = red_edges[0]
    blue_edges = blue_edges[0]

    red_wv_calib = make_wavecalib_pypeit.submit(red_arcs, red_edges, output_dir)
    blue_wv_calib = make_wavecalib_pypeit.submit(blue_arcs, blue_edges, output_dir)

    #return red_wv_calib, blue_wv_calib



