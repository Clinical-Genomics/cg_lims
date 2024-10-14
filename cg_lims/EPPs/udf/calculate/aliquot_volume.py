import logging
import sys
from typing import List

import click
from cg_lims import options
from cg_lims.exceptions import LimsError, LowVolumeError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts
from cg_lims.get.samples import get_one_sample_from_artifact
from genologics.entities import Artifact, Process

LOG = logging.getLogger(__name__)


def get_maximum_volume(process: Process, udf_name: str) -> float:
    """Return the maximum volume specified by the UDF <udf_name> in the process <process>"""
    max_volume: float = process.udf.get(udf_name)
    if not max_volume:
        raise MissingUDFsError(f"Process udf missing:{udf_name}")
    return max_volume


def get_artifact_udf(artifact: Artifact, udf_name: str) -> float:
    """Return the concentration specified by the UDF <udf_name> in the artifact <artifact>"""
    concentration: float = artifact.udf.get(udf_name)
    if not concentration:
        LOG.warning(
            f" UDF '{udf_name}' is missing for sample {get_one_sample_from_artifact(artifact=artifact).id}."
        )
    return concentration


def calculate_sample_volume(amount: float, concentration: float) -> float:
    """Calculate the volume of a sample given the amount needed and concentration."""
    return amount / concentration


def calculate_buffer_volume(max_volume: float, sample_volume: float) -> float:
    """Calculate the buffer volume of a sample given the max total volume and sample volume."""
    return max_volume - sample_volume


def set_volumes(
    artifact: Artifact,
    sample_volume_udf: str,
    buffer_volume_udf: str,
    sample_volume: float,
    buffer_volume: float,
) -> None:
    """Set sample UDFs."""
    artifact.udf[sample_volume_udf] = sample_volume
    artifact.udf[buffer_volume_udf] = buffer_volume
    artifact.put()


def volumes_below_threshold(
    minimum_volume: float, sample_volume: float, buffer_volume: float
) -> bool:
    """Check if volume aliquots are below the given threshold."""
    return sample_volume < minimum_volume or buffer_volume < minimum_volume


def calculate_volumes(
    artifacts: List[Artifact],
    process: Process,
    concentration_udf: str,
    sample_volume_udf: str,
    buffer_volume_udf: str,
    total_volume_udf: str,
    amount_needed_udf: str,
    minimum_limit: float,
):
    """Calculates volumes for diluting samples. The total volume differ depending on
    type of sample. It is given by the process udf <total_volume_udf>."""

    max_volume: float = get_maximum_volume(process=process, udf_name=total_volume_udf)
    samples_missing_udfs: List[str] = []
    samples_below_threshold: List[str] = []

    for art in artifacts:
        concentration: float = get_artifact_udf(artifact=art, udf_name=concentration_udf)
        amount: float = get_artifact_udf(artifact=art, udf_name=amount_needed_udf)

        if not amount or not concentration:
            samples_missing_udfs.append(get_one_sample_from_artifact(artifact=art).id)
            continue

        sample_volume: float = calculate_sample_volume(amount=amount, concentration=concentration)
        buffer_volume: float = calculate_buffer_volume(
            max_volume=max_volume, sample_volume=sample_volume
        )
        if volumes_below_threshold(
            minimum_volume=minimum_limit, sample_volume=sample_volume, buffer_volume=buffer_volume
        ):
            samples_below_threshold.append(get_one_sample_from_artifact(artifact=art).id)

        set_volumes(
            artifact=art,
            sample_volume_udf=sample_volume_udf,
            buffer_volume_udf=buffer_volume_udf,
            sample_volume=sample_volume,
            buffer_volume=buffer_volume,
        )

    if samples_missing_udfs:
        raise MissingUDFsError(
            f"Error: {len(samples_missing_udfs)} sample(s) are missing values for either '{concentration_udf}' or '{amount_needed_udf}' - {', '.join(samples_missing_udfs)}"
        )

    if samples_below_threshold:
        raise LowVolumeError(
            f"Warning: {len(samples_below_threshold)} sample(s) have aliquot volumes below {minimum_limit} µl - {', '.join(samples_below_threshold)}"
        )


@click.command()
@options.concentration_udf(help="Name of the concentration (ng/ul) artifact UDF")
@options.volume_udf(help="Name of the sample volume artifact UDF")
@options.buffer_udf(help="Name of the buffer volume artifact UDF")
@options.total_volume_udf(help="Name of the total volume process UDF")
@options.minimum_volume(
    help="The minimum volume (ul) allowed without sending a warning to the user."
)
@options.amount_ng_udf(
    help="Use if you want to overwrite the default UDF name 'Amount needed (ng)'"
)
@options.measurement(
    help="UDFs will be calculated and set on measurement artifacts. Use in QC steps."
)
@options.input(
    help="UDFs will be calculated ans set on input artifacts. Use non-output generating steps."
)
@click.pass_context
def aliquot_volume(
    ctx: click.Context,
    concentration_udf: str,
    volume_udf: str,
    buffer_udf: str,
    total_volume_udf: str,
    min_volume: str,
    amount_ng_udf: str = "Amount needed (ng)",
    measurement: bool = False,
    input: bool = False,
):
    """Calculates amount needed for samples."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process: Process = ctx.obj["process"]

    try:
        artifacts: List[Artifact] = get_artifacts(
            process=process, input=input, measurement=measurement
        )
        calculate_volumes(
            artifacts=artifacts,
            process=process,
            concentration_udf=concentration_udf,
            sample_volume_udf=volume_udf,
            buffer_volume_udf=buffer_udf,
            total_volume_udf=total_volume_udf,
            amount_needed_udf=amount_ng_udf,
            minimum_limit=float(min_volume),
        )
        message: str = "Volumes have been calculated for all samples."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
