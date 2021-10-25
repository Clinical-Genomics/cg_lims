"""CLI module for calculating beads volumes"""
import logging
import sys
from typing import List

import click
from genologics.entities import Artifact

from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts

LOG = logging.getLogger(__name__)

SAMPLE_VOLUME_BOUNDARY = 50.0
ELUTION_VOLUME = 40.0
ELUTION_VOLUME_FACTOR = 0.8


def calculate_elution_volume(sample_volume: float) -> float:
    """Calculates the elution volume based on the sample volume"""

    return (
        ELUTION_VOLUME
        if sample_volume < SAMPLE_VOLUME_BOUNDARY
        else ELUTION_VOLUME_FACTOR * sample_volume
    )


def calculate_water_volume(sample_volume: float) -> float:
    """Calculates the H20 volume based on the sample volume"""
    return (
        SAMPLE_VOLUME_BOUNDARY - sample_volume
        if sample_volume < SAMPLE_VOLUME_BOUNDARY
        else 0.0
    )


def calculate_beads_volume(sample_volume: float, h2o_volume: float) -> float:
    """Calculates the bead volume bases on sample volume and H2O volume"""
    return 2 * (sample_volume + h2o_volume)


def calculate_volumes(artifacts: List[Artifact]):
    """Calculates beads volume, water volume and elution volume"""

    missing_udfs = 0

    for artifact in artifacts:
        sample_volume: float = artifact.udf.get("Sample Volume (ul)")
        if sample_volume is None:
            missing_udfs += 1
            continue
        h2o_volume = calculate_water_volume(sample_volume)
        elution_volume = calculate_elution_volume(sample_volume)
        beads_volume = calculate_beads_volume(sample_volume, h2o_volume)
        artifact.udf["Volume Elution (ul)"] = elution_volume
        artifact.udf["Volume H2O (ul)"] = h2o_volume
        artifact.udf["Volume Beads (ul)"] = beads_volume
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
