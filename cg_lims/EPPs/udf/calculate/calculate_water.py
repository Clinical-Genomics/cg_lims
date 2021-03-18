import logging
import sys
from typing import List

import click
from genologics.entities import Artifact, Process

from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts

LOG = logging.getLogger(__name__)


def calculate_volumes(artifacts: List[Artifact], process: Process):
    """Calculates volumes of H2O for diluting samples. The total volume differ depending on
    type of sample. It is given by the process udf 'Total Volume (ul)'."""

    max_volume = process.udf.get("Total Volume (ul)")
    if not max_volume:
        raise MissingUDFsError("Process udf missing: Total Volume (ul)")

    missing_udfs = 0

    for artifact in artifacts:
        sample_volume = artifact.udf.get("Volume (ul)")

        if sample_volume is None:
            missing_udfs += 1
            continue
        volume_water = max_volume - sample_volume
        if volume_water < 0:
            volume_water = 0
        artifact.udf["Volume H2O (ul)"] = volume_water
        artifact.put()

    if missing_udfs:
        raise MissingUDFsError(f"Udf missing for {missing_udfs} samples")


@click.command()
@click.pass_context
def volume_water(ctx):
    """Calculates water volume for samples."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process = ctx.obj["process"]

    try:
        artifacts = get_artifacts(process=process, input=False)
        calculate_volumes(artifacts=artifacts, process=process)
        message = "Volume H2O have been calculated for all samples."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
