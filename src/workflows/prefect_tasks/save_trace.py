from prefect import task
from core.tracing import save_trace_solution

@task(name="Save Trace Solution")
def save_trace_solution_task(slit_positions, output_path: str):
    return save_trace_solution.fn(slit_positions, output_path)