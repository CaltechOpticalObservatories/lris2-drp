from prefect import task
from keckdrpframework.models.arguments import Arguments
from keck_primitives.qa_plot import GenerateQAPlot
from keck_primitives.utils import DummyAction, DummyContext


@task(name="Generate QA Plot")
def generate_qa_plot_task(data, output_path: str, title: str = "Flat QA"):
    args = Arguments()
    args["data"] = data
    args["output_path"] = output_path
    args["title"] = title

    action = DummyAction(args=args)
    context = DummyContext()

    result = GenerateQAPlot(action, context)._perform(args, config={})
    return result["output_path"]