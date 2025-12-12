from keckdrpframework.models.arguments import Arguments
from keckdrpframework.primitives.base_primitive import BasePrimitive
from core.flat import save_flat_fits


class SaveFlatFits(BasePrimitive):
    def __init__(self, action, context):
        super().__init__(action, context)

    def _perform(self, input_args: Arguments, config: dict) -> dict:
        """Save flat field results to a FITS file.

        By default saves the correction matrix. If original_data is provided,
        saves the corrected image instead.
        """
        correction = input_args["correction"]
        header = input_args["header"]
        output_path = input_args["output_path"]
        original_data = input_args["original_data"] if "original_data" in input_args else None

        result_path = save_flat_fits(correction, header, output_path, original_data)
        return {"output_path": result_path}
