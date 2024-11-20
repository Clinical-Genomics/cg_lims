import logging
import sys
from typing import List

import click
from cg_lims import options
from cg_lims.EPPs.udf.calculate.constants import SMRT_LINK_AVERAGE_MOLECULAR_WEIGHT_SS_DNA
from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts
from cg_lims.get.samples import get_one_sample_from_artifact
from genologics.entities import Artifact, Process

LOG = logging.getLogger(__name__)


def get_targeted_pooling_concentration(process: Process, udf_name: str) -> float:
    """Return the targeted pooling concentration from a process."""
    final_concentration: float = process.udf.get(udf_name)
    if not final_concentration or final_concentration == 0:
        raise MissingUDFsError("You need to specify a final loading concentration value above 0.")
    return final_concentration


def get_total_pooling_volume(process: Process, udf_name: str) -> float:
    """Return the total pooling volume from a process."""
    total_volume: float = process.udf.get(udf_name)
    if not total_volume or total_volume == 0:
        raise MissingUDFsError("You need to specify a final loading concentration value above 0.")
    return total_volume


def get_sample_concentration(artifact: Artifact, udf_name: str) -> float:
    """Return the total pooling volume from a process."""
    concentration: float = artifact.udf.get(udf_name)
    if not concentration or concentration == 0:
        raise MissingUDFsError(
            f"Sample {get_one_sample_from_artifact(artifact=artifact)} is missing an input concentration!"
        )
    return concentration


def get_sample_fragment_size(artifact: Artifact, udf_name: str) -> int:
    """Return the total pooling volume from a process."""
    size: int = artifact.udf.get(udf_name)
    if not size or size == 0:
        raise MissingUDFsError(
            f"Sample {get_one_sample_from_artifact(artifact=artifact)} is missing an average fragment size!"
        )
    return size


def convert_ngul_to_pm(ngul_conc: float, average_size: int) -> float:
    """Convert a given concentration from ng/ul to pM with the same formula that SMRT Link uses."""
    return 1e9 * ngul_conc / (2 * SMRT_LINK_AVERAGE_MOLECULAR_WEIGHT_SS_DNA * average_size)


def get_number_of_samples_in_pool(artifact: Artifact) -> int:
    """Return the number of samples in a given pool."""
    return len(artifact.samples)


def get_sample_aliquot_volume(
    target_concentration: float,
    target_volume: float,
    original_concentration: float,
    number_of_samples: int,
) -> float:
    """Return the sample aliquot volumes needed to pool a sample."""
    return (target_volume * target_concentration) / (number_of_samples * original_concentration)


def set_pooling_volumes(
    pool_artifact: Artifact,
    target_concentration: float,
    target_volume: float,
    size_udf: str,
    input_concentration_udf: str,
    sample_volume_udf: str,
    total_volume_udf: str,
    buffer_volume_udf: str,
) -> None:
    """Set the aliquot volumes needed for the pooling."""
    input_artifacts: List[Artifact] = pool_artifact.input_artifact_list()
    number_of_samples: int = get_number_of_samples_in_pool(artifact=pool_artifact)
    total_sample_volume: float = 0
    for input_artifact in input_artifacts:
        size: int = get_sample_fragment_size(artifact=input_artifact, udf_name=size_udf)
        input_concentration_ngul: float = get_sample_concentration(
            artifact=input_artifact, udf_name=input_concentration_udf
        )
        input_concentration_pm: float = convert_ngul_to_pm(
            ngul_conc=input_concentration_ngul, average_size=size
        )
        sample_volume: float = get_sample_aliquot_volume(
            target_concentration=target_concentration,
            target_volume=target_volume,
            original_concentration=input_concentration_pm,
            number_of_samples=number_of_samples,
        )
        total_sample_volume += sample_volume
        input_artifact.udf[sample_volume_udf] = sample_volume
        input_artifact.put()
    buffer_volume: float = target_volume - total_sample_volume
    pool_artifact.udf[total_volume_udf] = total_sample_volume
    pool_artifact.udf[buffer_volume_udf] = buffer_volume
    pool_artifact.put()


@click.command()
@options.concentration_udf()
@options.volume_udf()
@options.buffer_udf()
@options.total_volume_udf()
@options.size_udf()
@options.target_volume_udf()
@options.target_concentration_udf()
@click.pass_context
def revio_pooling(
    ctx: click.Context,
    concentration_udf: str,
    volume_udf: str,
    buffer_udf: str,
    total_volume_udf: str,
    size_udf: str,
    target_volume_udf: str,
    target_concentration_udf: str,
):
    """Calculate and set the pooling aliquots needed to prepare for Revio sequencing."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process: Process = ctx.obj["process"]

    try:
        artifacts: List[Artifact] = get_artifacts(process=process)
        target_volume: float = get_total_pooling_volume(process=process, udf_name=target_volume_udf)
        target_concentration: float = get_targeted_pooling_concentration(
            process=process, udf_name=target_concentration_udf
        )
        for artifact in artifacts:
            set_pooling_volumes(
                pool_artifact=artifact,
                target_volume=target_volume,
                target_concentration=target_concentration,
                size_udf=size_udf,
                input_concentration_udf=concentration_udf,
                sample_volume_udf=volume_udf,
                total_volume_udf=total_volume_udf,
                buffer_volume_udf=buffer_udf,
            )

        message: str = "Pooling volumes have been calculated for all artifacts!"
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
