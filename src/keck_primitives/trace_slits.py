from keckdrpframework.models.arguments import Arguments
from keckdrpframework.primitives.base_primitive import BasePrimitive
from core.tracing import trace_slits_1d


class TraceSlits1D(BasePrimitive):
    def __init__(self, action, context):
        super().__init__(action, context)

    def _perform(self, input_args: Arguments, config: dict) -> dict:
        data = input_args["flat_data"]
        slit_positions = trace_slits_1d(data)
        return {"slit_positions": slit_positions}
