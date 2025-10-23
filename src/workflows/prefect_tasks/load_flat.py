from prefect import task
from keckdrpframework.models.arguments import Arguments
from keck_primitives.load_flat import LoadFlat
from keck_primitives.utils import DummyAction, DummyContext


@task(name="Load Flat Frame")
def load_flat_frame_task(filepath: str):
    args = Arguments()
    args["filepath"] = filepath

    action = DummyAction(args=args)
    context = DummyContext()

    result = LoadFlat(action, context)._perform(args, config={})
    return result["flat_data"], result["header"]