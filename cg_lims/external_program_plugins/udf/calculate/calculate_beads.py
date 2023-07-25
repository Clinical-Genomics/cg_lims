"""CLI module for calculating beads volumes"""
import logging
import sys
from typing import List

import click
from genologics.entities import Artifact
from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts

LOG = logging.getLogger(__name__)


def calculate_elution_volume(sample_volume: float) -> float:
    """Calculates the elution volume. 80% of sample volume"""

    return 0.8 * sample_volume


def calculate_beads_volume(sample_volume: float) -> float:
    """Calculates the bead volume. Double of sample volume."""
    return 2 * sample_volume


def calculate_volumes(artifacts: List[Artifact]):
    """Calculates beads volume, water volume and elution volume"""

    missing_udfs = 0

    for artifact in artifacts:
        sample_volume: float = artifact.udf.get("Sample Volume (ul)")
        if sample_volume is None:
            missing_udfs += 1
            continue
        artifact.udf["Volume Elution (ul)"] = calculate_elution_volume(sample_volume)
        artifact.udf["Volume Beads (ul)"] = calculate_beads_volume(sample_volume)
        artifact.put()

    if missing_udfs:
        raise MissingUDFsError(
            f'Udf "Sample Volume (ul)" missing for {missing_udfs} out of {len(artifacts)} samples'
        )


@click.command()
@click.pass_context
def calculate_beads(context: click.Context):
    """Bead volume calculations for the step for Buffer Exchange TWIST"""

    LOG.info(f"Running {context.command_path} with params: {context.params}")

    process = context.obj["process"]

    try:
        artifacts: List[Artifact] = get_artifacts(process=process, input=False)
        calculate_volumes(artifacts=artifacts)
        message = "Beads volumes have been calculated."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
