import numpy as np
from scipy.signal import find_peaks
from keckdrpframework.models.arguments import Arguments
from keckdrpframework.primitives.base_primitive import BasePrimitive

class TraceSlits1D(BasePrimitive):
    def __init__(self, action, context):
        super().__init__(action, context)

    def _perform(self, input_args: Arguments, config: dict) -> dict:
        data = input_args["flat_data"]
        profile = np.median(data, axis=1)
        peaks, _ = find_peaks(profile, distance=20, prominence=0.05)
        return {"slit_positions": list(peaks)}
