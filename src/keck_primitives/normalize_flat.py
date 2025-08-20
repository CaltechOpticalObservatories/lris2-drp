import numpy as np
from keckdrpframework.models.arguments import Arguments
from keckdrpframework.primitives.base_primitive import BasePrimitive

class NormalizeFlat(BasePrimitive):
    def __init__(self, action, context):
        super().__init__(action, context)

    def _perform(self, input_args: Arguments, config: dict) -> dict:
        data = input_args["flat_data"]
        median = np.median(data[data > 0])
        norm = data / median
        return {"norm_data": norm}
