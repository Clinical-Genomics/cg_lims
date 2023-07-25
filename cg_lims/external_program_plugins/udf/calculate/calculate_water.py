"""CLI module for calculating beads volumes"""
import logging
import sys
from typing import List

import click
from genologics.entities import Artifact

from cg_lims import options
from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts

LOG = logging.getLogger(__name__)


def calculate_water_volume(sample_volume: float, sample_volume_limit: float) -> float:
    """Calculates the H20 volume based on the sample volume"""
    return sample_volume_limit - sample_volume if sample_volume < sample_volume_limit else 0.0


def calculate_volumes(artifacts: List[Artifact], sample_volume_limit: float):
    """Calculates water volume and total volume"""

    missing_udfs = 0
    high_volume_warning = False
    warning_message = ""
    for artifact in artifacts:
        sample_volume: float = artifact.udf.get("Sample Volume (ul)")
        if sample_volume is None:
            missing_udfs += 1
            continue
        h2o_volume = calculate_water_volume(
            sample_volume=sample_volume, sample_volume_limit=sample_volume_limit
        )
        total_volume = h2o_volume + sample_volume
        if total_volume > 100:
            high_volume_warning = True
        artifact.udf["Volume H2O (ul)"] = h2o_volume
        artifact.udf["Total Volume (uL)"] = total_volume
        artifact.put()

    if missing_udfs:
        warning_message += (
            f'Udf "Sample Volume (ul)" missing for {missing_udfs} out of {len(artifacts)} samples '
        )
    if high_volume_warning:
        warning_message += "Total volume higher than 100 ul for some samples!"
    if warning_message:
        raise MissingUDFsError(message=warning_message)


@click.command()
@options.sample_volume_limit()
@click.pass_context
def volume_water(context: click.Context, sample_volume_limit: float):
    """Water volume calculation."""

    LOG.info(f"Running {context.command_path} with params: {context.params}")

    process = context.obj["process"]

    try:
        artifacts: List[Artifact] = get_artifacts(process=process, input=False)
        calculate_volumes(artifacts=artifacts, sample_volume_limit=sample_volume_limit)
        message = "Beads volumes have been calculated."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
