import logging
import sys

import click
from cg_lims import options
from cg_lims.EPPs.files.smrt_link.models import RevioRun
from cg_lims.exceptions import LimsError
from genologics.entities import Process

LOG = logging.getLogger(__name__)


@click.command()
@options.file_placeholder()
@click.pass_context
def create_smrtlink_run_design(ctx, file: str):
    """Create pooling calculation .csv files for SMRT Link import."""
    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process: Process = ctx.obj["process"]

    try:
        revio_run: RevioRun = RevioRun(process=process)
        csv_string: str = revio_run.create_csv()
        with open(f"{file}_run_design.csv", "w") as file:
            file.write(csv_string)
        click.echo("The run design CSV was successfully generated.")
    except LimsError as e:
        sys.exit(e.message)
