from keckdrpframework.models.arguments import Arguments
from keckdrpframework.primitives.base_primitive import BasePrimitive
from core.tracing import save_trace_solution


class SaveTraceSolution(BasePrimitive):
    def __init__(self, action, context):
        super().__init__(action, context)

    def _perform(self, input_args: Arguments, config: dict) -> dict:
        """Save the traced slit positions to a text file."""
        slit_positions = input_args["slit_positions"]
        output_path = input_args["output_path"]

        result_path = save_trace_solution(slit_positions, output_path)
        return {"output_path": result_path}
