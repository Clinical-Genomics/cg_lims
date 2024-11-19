import logging
import sys
from typing import List, Optional

import click
from cg_lims import options
from cg_lims.exceptions import InvalidValueError, LimsError
from cg_lims.get.artifacts import get_artifacts
from cg_lims.get.udfs import (
    get_artifact_concentration,
    get_artifact_volume,
    get_final_concentration,
)
from genologics.entities import Artifact, Process

LOG = logging.getLogger(__name__)
failed_samples = []


def calculate_total_volume(
    final_concentration: float,
    sample_volume: float,
    sample_concentration: float,
    artifact: Artifact,
) -> float:
    """Calculate and return the total volume needed to reach the desired final concentration."""
    if final_concentration > sample_concentration:
        warning_message: str = (
            f"The final concentration ({final_concentration} ng/ul) is higher than the original one"
            f" ({sample_concentration} ng/ul) for sample {artifact.samples[0].id}. No dilution needed."
        )
        LOG.warning(warning_message)
        global failed_samples
        failed_samples.append(artifact.name)
        return sample_volume
    return (sample_volume * sample_concentration) / final_concentration


def calculate_buffer_volume(total_volume: float, sample_volume) -> float:
    """Calculate and return the buffer volume to dilute the sample with to the desired total volume"""
    return total_volume - sample_volume


def set_artifact_volumes(
    artifacts: List[Artifact],
    final_concentration: float,
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
        sample_volume: float = get_artifact_volume(
            artifact=artifact, sample_volume_udf=sample_volume_udf
        )
        total_volume: float = calculate_total_volume(
            final_concentration=final_concentration,
            artifact=artifact,
            sample_volume=sample_volume,
            sample_concentration=sample_concentration,
        )
        buffer_volume: float = calculate_buffer_volume(
            total_volume=total_volume, sample_volume=sample_volume
        )
        artifact.udf[buffer_volume_udf] = buffer_volume
        artifact.udf[total_volume_udf] = total_volume
        artifact.put()


@click.command()
@options.input()
@options.sample_udf(help="Name of sample volume UDF.")
@options.buffer_udf(help="Name of buffer volume UDF.")
@options.concentration_udf(help="Name of sample concentration UDF.")
@options.final_concentration_udf(help="Name of final target concentration UDF.")
@options.total_volume_udf(
    help="Name of total volume UDF on sample level. Note: Can't be combined with the process level alternative."
)
@click.pass_context
def library_normalization_revio(
    ctx: click.Context,
    input: bool,
    sample_udf: str,
    buffer_udf: str,
    concentration_udf: str,
    final_concentration_udf: str,
    total_volume_udf: Optional[str] = None,
) -> None:
    """Calculate the volumes for dilution for a set concentration with the total available sample volume"""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process: Process = ctx.obj["process"]
    artifacts: List[Artifact] = get_artifacts(process=process, input=input)
    try:
        final_concentration: float = get_final_concentration(
            process=process, final_concentration_udf=final_concentration_udf
        )
        set_artifact_volumes(
            artifacts=artifacts,
            final_concentration=final_concentration,
            total_volume_udf=total_volume_udf,
            sample_volume_udf=sample_udf,
            buffer_volume_udf=buffer_udf,
            concentration_udf=concentration_udf,
        )
        if failed_samples:
            failed_samples_string: str = ", ".join(failed_samples)
            error_message: str = (
                f"The following artifacts had a lower concentration than targeted: {failed_samples_string}"
            )
            LOG.error(error_message)
            raise InvalidValueError(error_message)
        message: str = "Volumes were successfully calculated."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
