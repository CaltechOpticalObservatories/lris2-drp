from keckdrpframework.models.arguments import Arguments
from keckdrpframework.primitives.base_primitive import BasePrimitive
from core.flat import load_flat_frame


class LoadFlat(BasePrimitive):
    def __init__(self, action, context):
        super().__init__(action, context)

    def _perform(self, input_args: Arguments, config: dict) -> dict:
        """Load a FITS file and return its data and header."""
        filepath = input_args["filepath"]
        data, header = load_flat_frame(filepath)
        return {"flat_data": data, "header": header}
