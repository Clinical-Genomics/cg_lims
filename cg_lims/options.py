import click


def process(help_string: str = "Lims id for current Process.") -> click.option:
    return click.option("-p", "--process", required=True, help=help_string)


def workflow_id(help_string: str = "Workflow id.") -> click.option:
    return click.option("-w", "--workflow-id", required=True, help=help_string)


def stage_id(help_string: str = "Stage id.") -> click.option:
    return click.option("-s", "--stage-id", required=True, help=help_string)


def udf(
    help_string: str = "UDF name",
) -> click.option:
    return click.option("-u", "--udf", required=True, help=help_string)

def log(
    help_string: str = "Path to log file.",
) -> click.option:
    return click.option("-l", "--log", required=True, help=help_string)

def input_artifacts(
    help_string: str = "Use this flag if you run the script from a QC step.",
) -> click.option:
    return click.option(
        "-i",
        "--input-artifacts",
        default=False,
        is_flag=True,
        help=help_string,
    )


def process_type(help_string: str = "Process type name.") -> click.option:
    return click.option(
        "-n",
        "--process-type",
        required=True,
        multiple=True,
        help=help_string,
    )
