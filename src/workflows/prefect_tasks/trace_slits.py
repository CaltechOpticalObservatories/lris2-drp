from prefect import task
from keck_primitives.trace_slits import TraceSlits1D
from keckdrpframework.models.arguments import Arguments
from keck_primitives.utils import DummyAction, DummyContext

@task(name="Trace Slits 1D")
def trace_slits_task(data):
    """Task to trace slits in 1D data."""
    args = Arguments()
    args["flat_data"] = data
    action = DummyAction(args=args)
    context = DummyContext()
    result = TraceSlits1D(action, context)._perform(args, config={})
    return result["slit_positions"]
