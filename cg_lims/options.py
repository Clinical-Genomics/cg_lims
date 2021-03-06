import click


def config(help: str = "config file for lims connection.") -> click.option:
    return click.option("-c", "--config", required=True, help=help)


def process(help: str = "Lims id for current Process.") -> click.option:
    return click.option("-p", "--process", required=True, help=help)


def log(
    help: str = "Path to log file.",
) -> click.option:
    return click.option("-l", "--log", required=True, help=help)


def workflow_id(help: str = "Workflow id.") -> click.option:
    return click.option("-w", "--workflow-id", required=True, help=help)


def stage_id(help: str = "Stage id.") -> click.option:
    return click.option("-s", "--stage-id", required=True, help=help)


def udf(
    help: str = "UDF name",
) -> click.option:
    return click.option("-u", "--udf", required=True, help=help)


def well_field(
    help: str = "Well field in file",
) -> click.option:
    return click.option("-wf", "--well-field", required=True, help=help)


def value_field(
    help: str = "Value field in file",
) -> click.option:
    return click.option("-vf", "--value-field", required=True, help=help)


def sample_qc_udf(
    help: str = "UDF name",
) -> click.option:
    return click.option("-qc", "--sample-qc-udf", default="", required=False, help=help)


def artifact_udf(
    help: str = "UDF name",
) -> click.option:
    return click.option("-audf", "--artifact-udf", required=True, help=help)


def sample_udf(
    help: str = "UDF name",
) -> click.option:
    return click.option("-sudf", "--sample-udf", required=True, help=help)


def process_udf(
    help: str = "UDF name",
) -> click.option:
    return click.option("-pudf", "--process-udf", required=True, help=help)


def file_placeholder(
    help: str = "File.",
) -> click.option:
    return click.option("-f", "--file", required=False, help=help)


def local_file(help="local file path for debug purposes.") -> click.option:
    return click.option("-lf", "--local_file", required=False, help=help)


def input(
    help: str = "Use this flag if you run the script from a QC step.",
) -> click.option:
    return click.option(
        "-i",
        "--input",
        default=False,
        is_flag=True,
        help=help,
    )


def measurement(
    help: str = "Use this flag if you run the script from a QC step and want "
    "to get the measurement artifacts.",
) -> click.option:
    return click.option(
        "-m",
        "--measurement",
        default=False,
        is_flag=True,
        help=help,
    )


def process_type(help: str = "Process type name.") -> click.option:
    return click.option(
        "-n",
        "--process-type",
        required=True,
        multiple=True,
        help=help,
    )


def file_extension(help: str = "Define file extension") -> click.option:
    return click.option("-e", "--extension", required=False, default="", help=help)


def amount_udf_option(help: str = "String of UDF used to get amount value") -> click.option:
    return click.option("--amount-udf", required=True, help=help)


def volume_udf_option(help: str = "String of UDF used to get volume value") -> click.option:
    return click.option("--volume-udf", required=True, help=help)


def concentration_udf_option(
    help: str = "String of UDF used to get concentration value",
) -> click.option:
    return click.option("--concentration-udf", required=True, help=help)
