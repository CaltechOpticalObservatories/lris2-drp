from prefect import task
from keckdrpframework.models.arguments import Arguments
from keck_primitives.save_trace import SaveTraceSolution
from keck_primitives.utils import DummyAction, DummyContext


@task(name="Save Trace Solution")
def save_trace_solution_task(slit_positions, output_path: str):
    args = Arguments()
    args["slit_positions"] = slit_positions
    args["output_path"] = output_path

    action = DummyAction(args=args)
    context = DummyContext()

    result = SaveTraceSolution(action, context)._perform(args, config={})
    return result["output_path"]
