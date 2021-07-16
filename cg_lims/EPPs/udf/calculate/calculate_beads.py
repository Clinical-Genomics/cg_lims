"""CLI module for calculating beads volumes"""
import logging
import sys
from typing import List

import click

from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts
from genologics.entities import Artifact

LOG = logging.getLogger(__name__)


def calculate_beads_volumes(artifacts: List[Artifact]):
    """Calculates beads volume, water volume and elution volume"""

    missing_udfs = 0

    for artifact in artifacts:
        sample_volume: float = artifact.udf.get("Sample Volume (ul)")
        if sample_volume is None:
            missing_udfs += 1
            continue
        if sample_volume < 50:
            h2o_volume = 50 - sample_volume
            elution_volume = 40
        else:
            h2o_volume = 0
            elution_volume = 0.8 * sample_volume
        beads_volume = 2 * (sample_volume + h2o_volume)
        artifact.udf["Volume Elution (ul)"] = elution_volume
        artifact.udf["Volume H2O (ul)"] = h2o_volume
        artifact.udf["Volume beads (ul)"] = beads_volume
        artifact.put()

    if missing_udfs:
        raise MissingUDFsError(f"Udf missing for {missing_udfs} samples")


@click.command()
@click.pass_context
def calculate_beads(context: click.Context):
    """Bead volume calculations for the step for Buffer Exchange TWIST (maybe more)"""  # TODO: # better docstring

    LOG.info(f"Running {context.command_path} with params: {context.params}")

    process = context.obj["process"]

    try:
        artifacts: List[Artifact] = get_artifacts(process=process, input=False)
        calculate_beads_volumes(artifacts=artifacts)
        message = "Beads volumes have been calculated."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
