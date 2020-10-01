import click


def process(help: str = "Lims id for current Process.") -> click.option:
    return click.option("-p", "--process", required=True, help=help)


def workflow_id(help: str = "Workflow id.") -> click.option:
    return click.option("-w", "--workflow-id", required=True, help=help)


def stage_id(help: str = "Stage id.") -> click.option:
    return click.option("-s", "--stage-id", required=True, help=help)


def udf(help: str = "UDF name",) -> click.option:
    return click.option("-u", "--udf", required=True, help=help)


def log(help: str = "Path to log file.",) -> click.option:
    return click.option("-l", "--log", required=True, help=help)


def input(
    help: str = "Use this flag if you run the script from a QC step.",
) -> click.option:
    return click.option(
        "-i", "--input", default=False, is_flag=True, help=help,
    )


def process_type(help: str = "Process type name.") -> click.option:
    return click.option(
        "-n", "--process-type", required=True, multiple=True, help=help,
    )
