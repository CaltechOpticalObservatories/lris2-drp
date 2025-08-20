from prefect import task
from core.flat import save_corrected_fits

@task(name="Save Corrected FITS")
def save_corrected_fits_task(original_data, correction, header, output_path: str):
    return save_corrected_fits.fn(original_data, correction, header, output_path)