from prefect import task
from core.qa import generate_qa_plot

@task(name="Generate QA Plot")
def generate_qa_plot_task(data, output_path: str, title: str = "Flat QA"):
    return generate_qa_plot.fn(data, output_path, title)