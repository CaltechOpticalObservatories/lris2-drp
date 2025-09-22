from prefect import task
from keckdrpframework.models.arguments import Arguments
from keck_primitives.normalize_flat import NormalizeFlat
from keck_primitives.utils import DummyAction, DummyContext


@task(name="Normalize Flat")
def normalize_flat_task(data):
    args = Arguments()
    args["flat_data"] = data

    action = DummyAction(args=args)
    context = DummyContext()

    result = NormalizeFlat(action, context)._perform(args, config={})
    return result["norm_data"]
