from keckdrpframework.models.arguments import Arguments
from keckdrpframework.primitives.base_primitive import BasePrimitive
from core.flat import save_corrected_fits


class SaveCorrectedFits(BasePrimitive):
    def __init__(self, action, context):
        super().__init__(action, context)

    def _perform(self, input_args: Arguments, config: dict) -> dict:
        """Apply the flat correction to the original data and save as a new FITS file."""
        original_data = input_args["original_data"]
        correction = input_args["correction"]
        header = input_args["header"]
        output_path = input_args["output_path"]

        result_path = save_corrected_fits(original_data, correction, header, output_path)
        return {"output_path": result_path}
