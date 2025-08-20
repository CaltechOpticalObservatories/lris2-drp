from prefect import task
from core.flat import create_flat_correction

@task(name="Create Flat Correction")
def create_flat_correction_task(norm_data):
    return create_flat_correction.fn(norm_data)