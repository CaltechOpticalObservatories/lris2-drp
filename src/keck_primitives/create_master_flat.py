from keckdrpframework.primitives.base_img import BaseImg
from core.flat import create_master_flat


class CreateMasterFlat(BaseImg):
    """
    Create a master flat correction

    This primitive wraps the create_master_flat function from core.flat.
    """

    def __init__(self, action, context):
        BaseImg.__init__(self, action, context)
        self.logger = context.pipeline_logger if hasattr(context, 'pipeline_logger') else None

    def _perform(self, args, config=None):
        """
        Create master flat correction.

        Args:
            args: Arguments object with:
                - flat_data: 2D numpy array of flat field data
                - slit_positions: Optional list of slit positions (for spectroscopic method)
                - slit_width: Width around slit centers (default: 50)
                - n_knots_spectral: Number of B-spline knots (default: 100)
                - low_signal_threshold: Threshold for masking low signal (default: 30.0)
                - edge_trim_pixels: Pixels to trim from slit edges (default: 5)

        Returns:
            Arguments object with:
                - correction: Master flat correction array
        """
        if config is None:
            config = {}

        flat_data = args["flat_data"]
        method = args["method"] if "method" in args else "spectroscopic"

        # Get optional parameters for spectroscopic method
        kwargs = {}
        if method == "spectroscopic":
            if "slit_positions" in args:
                kwargs["slit_positions"] = args["slit_positions"]
            kwargs["slit_width"] = args["slit_width"] if "slit_width" in args else 50
            kwargs["n_knots_spectral"] = args["n_knots_spectral"] if "n_knots_spectral" in args else 100
            kwargs["low_signal_threshold"] = args["low_signal_threshold"] if "low_signal_threshold" in args else 30.0
            kwargs["edge_trim_pixels"] = args["edge_trim_pixels"] if "edge_trim_pixels" in args else 5

        if self.logger:
            self.logger.info(f"Creating master flat using {method} method")

        # Create the master flat correction
        correction = create_master_flat(flat_data, **kwargs)

        if self.logger:
            self.logger.info(f"Master flat correction created successfully")

        return {"correction": correction}
