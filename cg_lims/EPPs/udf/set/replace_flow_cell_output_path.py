import logging
import sys
import click

from genologics.lims import Process
from cg_lims.exceptions import LimsError, MissingUDFsError

LOG = logging.getLogger(__name__)


def get_output_path(process: Process) -> str:
    """Return the output path UDF of the given process."""
    path: str = process.udf.get("Output Folder")
    if not path:
        LOG.error(f"Process {process.id} is missing UDF 'Output Folder'")
        raise MissingUDFsError(f"UDF: 'Output Folder' is missing from the step.")
    return path


def convert_output_path(path: str) -> str:
    """Return a corrected output path if needed. Can currently convert paths of the types:
    - \\<some novaseq windows network path>\clinicaldata\Runs\<run folder>
    - <windows hard drive>:\<run folder>\
    - //cg-nas.scilifelab.se/cg_data/seqdata/20230824_LH00217_0004_A225CW7LT3

    They are replaced with: \\130.237.80.51\Runs\<run folder>
    """
    new_path = path
    if ":\\" in path:
        new_path = "\\\\130.237.80.51\\Runs" + path.split(":")[1]
    elif "\\clinicaldata\\Runs\\" in path:
        new_path = "\\\\130.237.80.51\\Runs" + path.split("Runs")[1]
    elif "cg-nas.scilifelab.se/cg_data/seqdata/" in path:
        new_path = "\\\\130.237.80.51\\Runs\\" + path.split("seqdata/")[1]
    LOG.info(f"Original path '{path}' has been replaced with '{new_path}'.")
    return new_path


def replace_output_path(process: Process) -> None:
    """Replaces the output path of a process."""
    current_path = get_output_path(process=process)
    converted_path = convert_output_path(path=current_path)
    process.udf["Output Folder"] = converted_path
    process.put()


@click.command()
@click.pass_context
def replace_flow_cell_output_path(ctx):
    """Replaces the output path of flow cells."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process: Process = ctx.obj["process"]

    try:
        replace_output_path(process=process)
        message: str = "Output path has been successfully updated."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
