from prefect import task
from keckdrpframework.models.arguments import Arguments
from keck_primitives.create_master_flat import CreateMasterFlat
from keck_primitives.utils import DummyAction, DummyContext


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
    args = Arguments()
    args["flat_data"] = flat_data
    args["method"] = "spectroscopic"

    if slit_positions is not None:
        args["slit_positions"] = slit_positions
    args["slit_width"] = slit_width
    args["n_knots_spectral"] = n_knots_spectral
    args["low_signal_threshold"] = low_signal_threshold
    args["edge_trim_pixels"] = edge_trim_pixels

    action = DummyAction(args=args)
    context = DummyContext()

    result = CreateMasterFlat(action, context)._perform(args, config={})
    return result["correction"]
