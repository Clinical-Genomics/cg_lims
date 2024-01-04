import logging
import sys
from typing import List

import click
from genologics.entities import Artifact, Process
from typing import Optional

from cg_lims.exceptions import LimsError, InvalidValueError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts

LOG = logging.getLogger(__name__)
failed_samples = []

def get_final_concentration(process: Process, final_concentration_udf: str) -> float:
    """Return final concentration value from process."""
    final_concentration: Optional[float] = process.udf.get(final_concentration_udf)
    if not final_concentration:
        error_message: str = (
            f"Process {process.id} is missing a value for UDF '{final_concentration_udf}'."
        )
        LOG.error(error_message)
        raise MissingUDFsError(error_message)
    return final_concentration


def get_artifact_concentration(artifact: Artifact, concentration_udf: str) -> float:
    """Return concentration value from artifact."""
    concentration: Optional[float] = artifact.udf.get(concentration_udf)
    if not concentration:
        error_message: str = (
            f"Artifact {artifact.id} is missing a value for UDF '{concentration_udf}'."
        )
        LOG.error(error_message)
        raise MissingUDFsError(error_message)
    return concentration


def get_total_volume(artifact: Artifact, total_volume_udf: str) -> float:
    """Return total volume value from artifact."""
    total_volume: Optional[float] = artifact.udf.get(total_volume_udf)
    if not total_volume:
        error_message: str = (
            f"Artifact {artifact.id} is missing a value for UDF '{total_volume_udf}'."
        )
        LOG.error(error_message)
        raise MissingUDFsError(error_message)
    return total_volume


def calculate_sample_volume(
    final_concentration: float, artifact: Artifact
) -> float:
    """Calculate and return the sample volume needed to reach the desired final concentration."""
    sample_concentration: float = get_artifact_concentration(
        artifact=artifact, concentration_udf=concentration_udf
    )
    total_volume: float = get_total_volume(artifact=artifact, total_volume_udf=total_volume_udf)
    if final_concentration > sample_concentration:
        error_message: str = (
            f"The final concentration ({final_concentration} nM) is"
            f" higher than the original one ({sample_concentration} nM). No dilution needed."
        )
        LOG.error(error_message)
        global failed_samples
        failed_samples = failed_samples.append(artifact.samples[0].id)
        return total_volume
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
        concentration: float = get_artifact_concentration(
            artifact=artifact, concentration_udf=concentration_udf
        )
        total_volume: float = get_total_volume(artifact=artifact, total_volume_udf=total_volume_udf)
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
        final_concentration: float = get_final_concentration(
            process=process, final_concentration_udf="Final Concentration (nM)"
        )
        set_artifact_volumes(
            artifacts=artifacts,
            final_concentration=final_concentration,
            total_volume_udf="Total Volume (uL)",
            sample_volume_udf="Sample Volume (ul)",
            buffer_volume_udf="Volume Buffer (ul)",
            concentration_udf="Concentration (nM)",
        )
        if failed_samples:
            error_message = f"The following samples had a lower concentration than targeted: {failed_samples}"
            LOG.info(error_message)
            raise InvalidValueError(error_message)
        message: str = "Volumes were successfully calculated."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
