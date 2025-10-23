from prefect import task
from keckdrpframework.models.arguments import Arguments
from keck_primitives.save_corrected import SaveCorrectedFits
from keck_primitives.utils import DummyAction, DummyContext


@task(name="Save Corrected FITS")
def save_corrected_fits_task(original_data, correction, header, output_path: str):
    args = Arguments()
    args["original_data"] = original_data
    args["correction"] = correction
    args["header"] = header
    args["output_path"] = output_path

    action = DummyAction(args=args)
    context = DummyContext()

    result = SaveCorrectedFits(action, context)._perform(args, config={})
    return result["output_path"]