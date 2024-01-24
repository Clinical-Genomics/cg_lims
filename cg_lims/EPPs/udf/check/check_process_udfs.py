import logging
import sys
from typing import List

import click
from cg_lims import options
from cg_lims.exceptions import LimsError, MissingUDFsError
from genologics.entities import Process

LOG = logging.getLogger(__name__)


def check_udfs(process: Process, process_udfs: List[str]) -> None:
    """Check that process UDFs are set."""

    warning = []
    for udf in process_udfs:
        if process.udf.get(udf) is None:
            warning.append(f"UDF: '{udf}' is missing for the step.")
    if warning:
        LOG.warning(" ".join(warning))
        raise MissingUDFsError(message=" ".join(warning))
    LOG.info("Process UDFs were all set.")


@click.command()
@options.process_udfs()
@click.pass_context
def check_process_udfs(
    ctx: click.Context,
    process_udfs: List[str],
):
    """Script to check that process UDFs are set."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process: Process = ctx.obj["process"]
    try:
        check_udfs(process=process, process_udfs=process_udfs)
        click.echo("Process UDFs were checked.")
    except LimsError as e:
        sys.exit(e.message)
