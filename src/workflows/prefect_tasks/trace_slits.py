from prefect import task
from core.tracing import trace_slits_1d


@task(name="Trace Slits 1D")
def trace_slits_task(data):
    """Task to trace slits in 1D data."""
    slit_positions = trace_slits_1d(data)
    return slit_positions
