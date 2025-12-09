from prefect import task
from keckdrpframework.models.arguments import Arguments
from keck_primitives.save_correction import SaveCorrectionFits
from keck_primitives.utils import DummyAction, DummyContext


@task(name="Save Correction FITS")
def save_correction_fits_task(correction, header, output_path: str):
    args = Arguments()
    args["correction"] = correction
    args["header"] = header
    args["output_path"] = output_path

    action = DummyAction(args=args)
    context = DummyContext()

    result = SaveCorrectionFits(action, context)._perform(args, config={})
    return result["output_path"]
