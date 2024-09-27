"""CLI module for calculating beads volumes"""

import logging
import sys
from typing import List

import click
from cg_lims import options
from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts
from genologics.entities import Artifact

LOG = logging.getLogger(__name__)


def calculate_buffer_volume(sample_volume: float, sample_volume_limit: float) -> float:
    """Calculates the buffer volume based on the sample volume"""
    return sample_volume_limit - sample_volume if sample_volume < sample_volume_limit else 0.0


def calculate_volumes(
    artifacts: List[Artifact],
    total_volume_udf: str,
    volume_udf: str,
    buffer_udf: str,
    sample_volume_limit: float,
):
    """Calculates buffer volume and total volume"""

    missing_udfs = 0
    high_volume_warning = False
    warning_message = ""
    for artifact in artifacts:
        sample_volume: float = artifact.udf.get(volume_udf)
        if sample_volume is None:
            missing_udfs += 1
            continue
        buffer_volume = calculate_buffer_volume(
            sample_volume=sample_volume, sample_volume_limit=sample_volume_limit
        )
        total_volume = buffer_volume + sample_volume
        if total_volume > sample_volume_limit:
            high_volume_warning = True
        artifact.udf[buffer_udf] = buffer_volume
        artifact.udf[total_volume_udf] = total_volume
        artifact.put()

    if missing_udfs:
        warning_message += (
            f'Udf "Sample Volume (ul)" missing for {missing_udfs} out of {len(artifacts)} samples '
        )
    if high_volume_warning:
        warning_message += f"Total volume higher than {sample_volume_limit} ul for some samples!"
    if warning_message:
        raise MissingUDFsError(message=warning_message)


@click.command()
@options.total_volume_udf()
@options.volume_udf()
@options.buffer_udf()
@options.sample_volume_limit()
@click.pass_context
def volume_buffer(
    context: click.Context,
    total_volume_udf: str,
    volume_udf: str,
    buffer_udf: str,
    sample_volume_limit: float,
):
    """Buffer volume calculation."""

    LOG.info(f"Running {context.command_path} with params: {context.params}")

    process = context.obj["process"]

    try:
        artifacts: List[Artifact] = get_artifacts(process=process, input=False)
        calculate_volumes(
            artifacts=artifacts,
            total_volume_udf=total_volume_udf,
            volume_udf=volume_udf,
            buffer_udf=buffer_udf,
            sample_volume_limit=sample_volume_limit,
        )
        message = "Volumes have been calculated."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
