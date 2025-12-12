from prefect import task
from keckdrpframework.models.arguments import Arguments
from keck_primitives.save_correction import SaveFlatFits
from keck_primitives.utils import DummyAction, DummyContext


@task(name="Save Flat FITS")
def save_flat_fits_task(correction, header, output_path: str, original_data=None):
    """Save flat field results to a FITS file.

    By default saves the correction matrix. If original_data is provided,
    saves the corrected image instead.
    """
    args = Arguments()
    args["correction"] = correction
    args["header"] = header
    args["output_path"] = output_path
    if original_data is not None:
        args["original_data"] = original_data

    action = DummyAction(args=args)
    context = DummyContext()

    result = SaveFlatFits(action, context)._perform(args, config={})
    return result["output_path"]
