from keckdrpframework.models.arguments import Arguments
from keckdrpframework.primitives.base_primitive import BasePrimitive
from core.flat import save_correction_fits


class SaveCorrectionFits(BasePrimitive):
    def __init__(self, action, context):
        super().__init__(action, context)

    def _perform(self, input_args: Arguments, config: dict) -> dict:
        """Save the flat field correction map to a FITS file."""
        correction = input_args["correction"]
        header = input_args["header"]
        output_path = input_args["output_path"]

        result_path = save_correction_fits(correction, header, output_path)
        return {"output_path": result_path}
