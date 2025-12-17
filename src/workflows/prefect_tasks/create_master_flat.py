from prefect import task
from core.flat import create_master_flat


@task(name="Create Master Flat")
def create_master_flat_task(
    flat_data,
    slit_positions=None,
    slit_width=50,
    n_knots_spectral=100,
    low_signal_threshold=30.0,
    edge_trim_pixels=5
):
    """
    Create master flat correction using spectroscopic method.

    Args:
        flat_data: 2D numpy array of flat field data
        slit_positions: Optional list of slit positions (None = auto-detect)
        slit_width: Width around slit centers in pixels
        n_knots_spectral: Number of B-spline knots for spectral fitting
        low_signal_threshold: Pixels below this value get no correction
        edge_trim_pixels: Number of pixels to trim from slit edges

    Returns:
        Master flat correction array (multiply science data by this)
    """
    correction = create_master_flat(
        flat_data,
        slit_positions=slit_positions,
        slit_width=slit_width,
        n_knots_spectral=n_knots_spectral,
        low_signal_threshold=low_signal_threshold,
        edge_trim_pixels=edge_trim_pixels
    )
    return correction
