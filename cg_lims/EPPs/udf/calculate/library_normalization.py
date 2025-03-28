import logging
import sys
from typing import List, Optional

import click
from cg_lims import options
from cg_lims.exceptions import InvalidValueError, LimsError, MissingValueError, LowVolumeError
from cg_lims.get.artifacts import get_artifacts
from cg_lims.get.samples import get_one_sample_from_artifact
from cg_lims.get.udfs import (
    get_artifact_concentration,
    get_final_concentration,
    get_process_total_volume,
    get_total_volume,
)
from genologics.entities import Artifact, Process

LOG = logging.getLogger(__name__)
failed_samples = []
samples_below_threshold: List[str] = []


def calculate_sample_volume(
    final_concentration: float,
    total_volume: float,
    sample_concentration: float,
    sample_volume_limit: Optional[str],
    sample_id: str,
) -> float:
    """Calculate and return the sample volume needed to reach the desired final concentration."""
    if final_concentration > sample_concentration:
        warning_message: str = (
            f"The final concentration is higher than the original one for sample {sample_id}. No dilution needed."
        )
        LOG.warning(warning_message)
        global failed_samples
        failed_samples.append(sample_id)
        return float(sample_volume_limit) if sample_volume_limit else total_volume
    return (final_concentration * total_volume) / sample_concentration


def calculate_buffer_volume(total_volume: float, sample_volume: float, sample_id: str) -> float:
    """Calculate and return the buffer volume needed to reach the desired total volume."""
    if sample_volume > total_volume:
        LOG.info(
            f"Sample volume is already larger than the total one. Setting buffer volume to 0 ul."
        )
        return 0
    elif sample_id in failed_samples:
        return 0
    return total_volume - sample_volume


def volumes_below_threshold(
    minimum_volume: float, sample_volume: float, buffer_volume: float
) -> bool:
    """Check if volume aliquots are below the given threshold."""
    return (sample_volume < minimum_volume) or (
        buffer_volume != 0 and buffer_volume < minimum_volume
    )


def set_artifact_volumes(
    artifacts: List[Artifact],
    final_concentration: float,
    set_total_volume: Optional[float],
    total_volume_udf: Optional[str],
    sample_volume_udf: str,
    buffer_volume_udf: str,
    concentration_udf: str,
    sample_volume_limit: Optional[str],
    minimum_limit: float,
) -> None:
    """Set volume UDFs on artifact level, given a list of artifacts, final concentration, and UDF names."""

    for artifact in artifacts:
        sample_id: str = artifact.samples[0].id
        sample_concentration: float = get_artifact_concentration(
            artifact=artifact, concentration_udf=concentration_udf
        )
        if not total_volume_udf and not set_total_volume:
            error_message = (
                "The calculation needs either a total volume value or UDF name to be given!"
            )
            LOG.error(error_message)
            raise MissingValueError(error_message)
        elif set_total_volume:
            total_volume: float = set_total_volume
        else:
            total_volume: float = get_total_volume(
                artifact=artifact, total_volume_udf=total_volume_udf
            )
        sample_volume: float = calculate_sample_volume(
            final_concentration=final_concentration,
            total_volume=total_volume,
            sample_concentration=sample_concentration,
            sample_volume_limit=sample_volume_limit,
            sample_id=sample_id,
        )
        buffer_volume: float = calculate_buffer_volume(
            total_volume=total_volume,
            sample_volume=sample_volume,
            sample_id=sample_id,
        )
        artifact.udf[sample_volume_udf] = sample_volume
        artifact.udf[buffer_volume_udf] = buffer_volume
        if sample_id in failed_samples and sample_volume_limit:
            artifact.udf[total_volume_udf] = sample_volume
        artifact.put()

        if volumes_below_threshold(
            minimum_volume=minimum_limit,
            sample_volume=round(sample_volume, 2),
            buffer_volume=round(buffer_volume, 2),
        ):
            samples_below_threshold.append(get_one_sample_from_artifact(artifact=artifact).id)


@click.command()
@options.input()
@options.sample_udf(help="Name of sample volume UDF.")
@options.buffer_udf(help="Name of buffer volume UDF.")
@options.concentration_udf(help="Name of sample concentration UDF.")
@options.final_concentration_udf(help="Name of final target concentration UDF.")
@options.minimum_volume(
    help="The minimum volume (ul) allowed without sending a warning to the user. Default is 0."
)
@options.sample_volume_limit(help="The available volume of a sample.")
@options.total_volume_udf(
    help="Name of total volume UDF on sample level. Note: Can't be combined with the process level alternative."
)
@options.total_volume_process_udf(
    help="Name of total volume UDF on process level. Note: Can't be combined with the sample level alternative."
)
@click.pass_context
def library_normalization(
    ctx: click.Context,
    input: bool,
    sample_udf: str,
    buffer_udf: str,
    concentration_udf: str,
    final_concentration_udf: str,
    min_volume: str = 0,
    sample_volume_limit: Optional[str] = None,
    total_volume_udf: Optional[str] = None,
    total_volume_pudf: Optional[str] = None,
) -> None:
    """Calculate and set volumes needed for normalization of sample or pool before sequencing."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process: Process = ctx.obj["process"]
    artifacts: List[Artifact] = get_artifacts(process=process, input=input)
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
            set_total_volume=total_volume,
            total_volume_udf=total_volume_udf,
            sample_volume_udf=sample_udf,
            buffer_volume_udf=buffer_udf,
            concentration_udf=concentration_udf,
            sample_volume_limit=sample_volume_limit,
            minimum_limit=float(min_volume),
        )
        if samples_below_threshold:
            raise LowVolumeError(
                f"Warning: {len(samples_below_threshold)} sample(s) have aliquot volumes below {min_volume} µl - {', '.join(samples_below_threshold)}"
            )
        if failed_samples:
            failed_samples_string: str = ", ".join(failed_samples)
            error_message: str = (
                f"The following artifacts had a lower concentration than targeted: {failed_samples_string}"
            )
            LOG.info(error_message)
            raise InvalidValueError(error_message)
        message: str = "Volumes were successfully calculated."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
