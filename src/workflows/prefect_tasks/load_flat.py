from prefect import task
from core.flat import load_flat_frame

@task(name="Load Flat Frame")
def load_flat_frame_task(filepath: str):
    return load_flat_frame.fn(filepath)