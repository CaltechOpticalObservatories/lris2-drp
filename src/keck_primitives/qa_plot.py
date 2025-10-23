from keckdrpframework.models.arguments import Arguments
from keckdrpframework.primitives.base_primitive import BasePrimitive
from core.qa import generate_qa_plot


class GenerateQAPlot(BasePrimitive):
    def __init__(self, action, context):
        super().__init__(action, context)

    def _perform(self, input_args: Arguments, config: dict) -> dict:
        """Generate a QA plot for the normalized flat field data."""
        data = input_args["data"]
        output_path = input_args["output_path"]
        title = input_args["title"] if "title" in input_args else "Flat QA"

        result_path = generate_qa_plot(data, output_path, title)
        return {"output_path": result_path}
