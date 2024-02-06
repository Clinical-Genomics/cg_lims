import logging
import sys
from datetime import date

import click
from cg_lims.exceptions import LimsError
from genologics.lims import Process

LOG = logging.getLogger(__name__)


def get_experiment_name(process: Process) -> str:
    """"""
    return f"{date.today()}_{process.id}"


def set_experiment_name(process: Process) -> None:
    """"""
    process.udf["Experiment Name"] = get_experiment_name(process=process)
    process.put()


@click.command()
@click.pass_context
def set_ont_sequencing_settings(ctx):
    """Sets the settings required for sequencing of ONT flow cells."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process: Process = ctx.obj["process"]

    try:
        set_experiment_name(process=process)
        message: str = "Sequencing settings have been successfully set."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
