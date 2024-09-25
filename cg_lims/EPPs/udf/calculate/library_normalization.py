import logging
import sys
from typing import List, Optional

import click
from cg_lims import options
from cg_lims.exceptions import InvalidValueError, LimsError, MissingValueError
from cg_lims.get.artifacts import get_artifacts
from cg_lims.get.udfs import get_udf
from genologics.entities import Artifact, Process

LOG = logging.getLogger(__name__)
failed_samples = []


def get_final_concentration(process: Process, final_concentration_udf: str) -> float:
    """Return final concentration value from process."""
    return float(get_udf(entity=process, udf=final_concentration_udf))


def get_artifact_concentration(artifact: Artifact, concentration_udf: str) -> float:
    """Return concentration value from artifact."""
    return float(get_udf(entity=artifact, udf=concentration_udf))


def get_total_volume(artifact: Artifact, total_volume_udf: str) -> float:
    """Return total volume value from artifact."""
    return float(get_udf(entity=artifact, udf=total_volume_udf))


def get_process_total_volume(process: Process, total_volume_udf: str) -> Optional[float]:
    """Return total volume value from process."""
    return process.udf.get(total_volume_udf)


def calculate_sample_volume(
    final_concentration: float, total_volume: float, sample_concentration: float, artifact: Artifact
) -> float:
    """Calculate and return the sample volume needed to reach the desired final concentration."""
    if final_concentration > sample_concentration:
        error_message: str = (
            f"The final concentration ({final_concentration} nM) is higher than the original one"
            f" ({sample_concentration} nM) for sample {artifact.samples[0].id}. No dilution needed."
        )
        LOG.error(error_message)
        global failed_samples
        failed_samples.append(artifact.name)
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
    total_volume: Optional[float],
    total_volume_udf: Optional[str],
    sample_volume_udf: str,
    buffer_volume_udf: str,
    concentration_udf: str,
) -> None:
    """Set volume UDFs on artifact level, given a list of artifacts, final concentration, and UDF names."""
    for artifact in artifacts:
        sample_concentration: float = get_artifact_concentration(
            artifact=artifact, concentration_udf=concentration_udf
        )
        if total_volume_udf and not total_volume:
            total_volume: float = get_total_volume(
                artifact=artifact, total_volume_udf=total_volume_udf
            )
        else:
            error_message = (
                "The calculation needs either a total volume value or UDF name to be given!"
            )
            LOG.error(error_message)
            raise MissingValueError(error_message)
        sample_volume: float = calculate_sample_volume(
            final_concentration=final_concentration,
            artifact=artifact,
            total_volume=total_volume,
            sample_concentration=sample_concentration,
        )
        buffer_volume: float = calculate_buffer_volume(
            total_volume=total_volume, sample_volume=sample_volume
        )
        artifact.udf[sample_volume_udf] = sample_volume
        artifact.udf[buffer_volume_udf] = buffer_volume
        artifact.put()


@click.command()
@options.sample_udf
@options.buffer_udf
@options.concentration_udf
@options.final_concentration_udf
@options.total_volume_udf
@options.total_volume_process_udf
@click.pass_context
def library_normalization(
    ctx: click.Context,
    sample_udf: str,
    buffer_udf: str,
    concentration_udf: str,
    final_concentration_udf: str,
    total_volume_udf: Optional[str] = None,
    total_volume_pudf: Optional[str] = None,
) -> None:
    """Calculate and set volumes needed for normalization of pool before sequencing."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process: Process = ctx.obj["process"]
    artifacts: List[Artifact] = get_artifacts(process=process)
    try:
        final_concentration: float = get_final_concentration(
            process=process, final_concentration_udf=final_concentration_udf
        )
        if total_volume_pudf:
            total_volume: Optional[float] = get_process_total_volume(
                process=process, total_volume_udf=total_volume_pudf
            )
        else:
            total_volume = None
        set_artifact_volumes(
            artifacts=artifacts,
            final_concentration=final_concentration,
            total_volume=total_volume,
            total_volume_udf=total_volume_udf,
            sample_volume_udf=sample_udf,
            buffer_volume_udf=buffer_udf,
            concentration_udf=concentration_udf,
        )
        if failed_samples:
            failed_samples_string = ", ".join(failed_samples)
            error_message = f"The following artifacts had a lower concentration than targeted: {failed_samples_string}"
            LOG.info(error_message)
            raise InvalidValueError(error_message)
        message: str = "Volumes were successfully calculated."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
