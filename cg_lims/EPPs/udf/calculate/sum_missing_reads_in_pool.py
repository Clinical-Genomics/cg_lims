import logging
import sys
from typing import Tuple

import click

from cg_lims.exceptions import LimsError
from cg_lims.get.artifacts import get_artifacts

LOG = logging.getLogger(__name__)


def sum_reads_in_pool(artifacts: list) -> Tuple[int, int]:
    """Summing the missing reads for all samples in one pool."""

    failed_arts = 0
    passed_arts = 0

    for artifact in artifacts:
        if len(artifact.samples) == 1:
            continue

        missing_reads_pool = []
        for sample in artifact.samples:
            if sample.udf.get("Reads missing (M)") is None:
                failed_arts += 1
                missing_reads_pool = []
                break
            missing_reads_pool.append(sample.udf["Reads missing (M)"])
        if missing_reads_pool:
            artifact.udf["Missing reads Pool (M)"] = sum(missing_reads_pool)
            artifact.put()
            passed_arts += 1
    return passed_arts, failed_arts


@click.command()
@click.pass_context
def missing_reads_in_pool(ctx):
    """Script to calculate missing reads in a pool"""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process = ctx.obj["process"]

    try:
        artifacts = get_artifacts(process=process, input=False)
        passed_arts, failed_arts = sum_reads_in_pool(artifacts=artifacts)
        message = f"Updated {passed_arts}. Ignored {failed_arts} due to missing Sample UDFs: 'Reads missing (M)'"
        if failed_arts:
            LOG.error(message)
            sys.exit(message)
        else:
            LOG.info(message)
            click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
