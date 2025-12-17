from prefect import task
from core.qa import generate_qa_plot


@task(name="Generate QA Plot")
def generate_qa_plot_task(data, output_path: str, title: str = "Flat QA"):
    output_path = generate_qa_plot(data, output_path, title)
    return output_path
