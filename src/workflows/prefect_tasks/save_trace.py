from prefect import task
from core.tracing import save_trace_solution


@task(name="Save Trace Solution")
def save_trace_solution_task(slit_positions, output_path: str):
    output_path = save_trace_solution(slit_positions, output_path)
    return output_path
