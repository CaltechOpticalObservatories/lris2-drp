from prefect import task
from core.flat import save_corrected_fits


@task(name="Save Corrected FITS")
def save_corrected_fits_task(original_data, correction, header, output_path: str):
    output_path = save_corrected_fits(original_data, correction, header, output_path)
    return output_path
