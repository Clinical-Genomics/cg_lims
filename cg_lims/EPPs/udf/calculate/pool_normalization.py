import logging
import sys
from typing import List

import click
from genologics.entities import Artifact, Process

from cg_lims.exceptions import LimsError, InvalidValueError
from cg_lims.get.artifacts import get_artifacts

LOG = logging.getLogger(__name__)


def calculate_sample_volume(
    final_concentration: float, total_volume: float, sample_concentration: float
) -> float:
    """Calculate and return the sample volume needed to reach the desired final concentration."""
    if final_concentration > sample_concentration:
        error_message: str = f"The final concentration ({final_concentration} nM) can't be higher than the original one ({sample_concentration} nM)."
        LOG.error(error_message)
        raise InvalidValueError(error_message)
    return (final_concentration * total_volume) / sample_concentration


def calculate_buffer_volume(total_volume: float, sample_volume: float) -> float:
    """Calculate and return the buffer volume needed to reach the desired total volume."""
    if sample_volume > total_volume:
        LOG.info(
            f"Sample volume is already larger than the total one. Setting buffer volume to 0 ul."
        )
        return 0
    return total_volume - sample_volume


def set_artifact_volumes(
    artifacts: List[Artifact],
    final_concentration: float,
    total_volume_udf: str,
    sample_volume_udf: str,
    buffer_volume_udf: str,
    concentration_udf: str,
) -> None:
    """Set volume UDFs on artifact level, given a list of artifacts, final concentration, and UDF names."""
    for artifact in artifacts:
        concentration: float = artifact.udf.get(concentration_udf)
        total_volume: float = artifact.udf.get(total_volume_udf)
        sample_volume: float = calculate_sample_volume(
            final_concentration=final_concentration,
            total_volume=total_volume,
            sample_concentration=concentration,
        )
        buffer_volume: float = calculate_buffer_volume(
            total_volume=total_volume, sample_volume=sample_volume
        )
        artifact.udf[sample_volume_udf] = sample_volume
        artifact.udf[buffer_volume_udf] = buffer_volume
        artifact.put()


@click.command()
@click.pass_context
def pool_normalization(ctx: click.Context):
    """Calculate and set volumes needed for normalization of pool before sequencing."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process: Process = ctx.obj["process"]
    artifacts: List[Artifact] = get_artifacts(process=process)
    try:
        final_concentration: float = process.udf.get("Final Concentration (nM)")
        set_artifact_volumes(
            artifacts=artifacts,
            final_concentration=final_concentration,
            total_volume_udf="Total Volume (uL)",
            sample_volume_udf="Sample Volume (ul)",
            buffer_volume_udf="Volume Buffer (ul)",
            concentration_udf="Concentration (nM)",
        )
        message: str = "Volumes were successfully calculated and set."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
