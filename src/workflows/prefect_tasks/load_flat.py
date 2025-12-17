from prefect import task
from core.flat import load_flat_frame


@task(name="Load Flat Frame")
def load_flat_frame_task(filepath: str):
    flat_data, header = load_flat_frame(filepath)
    return flat_data, header
