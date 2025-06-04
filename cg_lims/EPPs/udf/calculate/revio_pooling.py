import logging
import sys
from typing import Any, List

import click
from cg_lims import options
from cg_lims.EPPs.udf.calculate.constants import SMRT_LINK_AVERAGE_MOLECULAR_WEIGHT_SS_DNA
from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts
from genologics.entities import Artifact, Process

LOG = logging.getLogger(__name__)


def get_total_pooling_volume(
    process: Process, artifact: Artifact, volume_udf_name: str, nr_smrt_cells_udf: str
) -> float:
    """Return the total pooling volume from a process."""
    volume_per_smrt_cell: float = process.udf.get(volume_udf_name)
    nr_smrt_cells: int = get_numeric_artifact_udf(artifact=artifact, udf_name=nr_smrt_cells_udf)
    total_volume: float = volume_per_smrt_cell * nr_smrt_cells
    if not total_volume or total_volume == 0:
        raise MissingUDFsError("You need to specify a pool volume above 0 ul.")
    return total_volume


def get_numeric_artifact_udf(artifact: Artifact, udf_name: str) -> Any:
    """Return the numeric UDF value from a given artifact"""
    value: Any = artifact.udf.get(udf_name)
    if not value or value == 0:
        raise MissingUDFsError(
            f"Artifact {artifact.name} is missing a value for the UDF {udf_name}!"
        )
    return value


def convert_ngul_to_pm(ngul_conc: float, average_size: int) -> float:
    """Convert a given concentration from ng/ul to pM with the same formula that SMRT Link uses."""
    print(f"Original conc: {ngul_conc} ng/ul")
    print(f"Avg mol weight SS DNA: {SMRT_LINK_AVERAGE_MOLECULAR_WEIGHT_SS_DNA}")
    print(f"Avg Size: {average_size} bp")
    return 1e9 * ngul_conc / (2 * SMRT_LINK_AVERAGE_MOLECULAR_WEIGHT_SS_DNA * average_size)


def get_number_of_pool_inputs(artifact: Artifact) -> int:
    """Return the number of samples in a given pool."""
    return len(artifact.input_artifact_list())


def get_sample_aliquot_volume(
    target_concentration: float,
    target_volume: float,
    original_concentration: float,
    number_of_inputs: int,
) -> float:
    """Return the sample aliquot volumes needed to pool a sample."""
    print(f"Target vol: {target_volume} ul")
    print(f"Target conc: {target_concentration} pM")
    print(f"Number of inputs: {number_of_inputs}")
    print(f"Original conc: {original_concentration} pM")
    return (target_volume * target_concentration) / (number_of_inputs * original_concentration)


def set_pooling_volumes(
    pool_artifact: Artifact,
    target_concentration: float,
    target_volume: float,
    control_volume: float,
    size_udf: str,
    input_concentration_udf: str,
    sample_volume_udf: str,
    total_volume_udf: str,
    buffer_volume_udf: str,
    control_volume_udf: str,
) -> None:
    """Set the aliquot volumes needed for the pooling."""
    input_artifacts: List[Artifact] = pool_artifact.input_artifact_list()
    number_of_inputs: int = get_number_of_pool_inputs(artifact=pool_artifact)
    total_sample_volume: float = 0
    for input_artifact in input_artifacts:
        size: int = get_numeric_artifact_udf(artifact=input_artifact, udf_name=size_udf)
        input_concentration_ngul: float = get_numeric_artifact_udf(
            artifact=input_artifact, udf_name=input_concentration_udf
        )
        input_concentration_pm: float = convert_ngul_to_pm(
            ngul_conc=input_concentration_ngul, average_size=size
        )
        sample_volume: float = get_sample_aliquot_volume(
            target_concentration=target_concentration,
            target_volume=target_volume,
            original_concentration=input_concentration_pm,
            number_of_inputs=number_of_inputs,
        )
        total_sample_volume += sample_volume
        input_artifact.udf[sample_volume_udf] = sample_volume
        input_artifact.put()
    buffer_volume: float = target_volume - total_sample_volume
    pool_artifact.udf[total_volume_udf] = total_sample_volume
    pool_artifact.udf[buffer_volume_udf] = buffer_volume
    pool_artifact.udf[control_volume_udf] = control_volume
    pool_artifact.put()


@click.command()
@options.concentration_udf()
@options.volume_udf()
@options.buffer_udf()
@options.total_volume_udf()
@options.size_udf()
@options.target_volume_udf()
@options.target_concentration_udf()
@options.sequencing_container_udf()
@options.control_volume_udf()
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
    sequencing_container_udf: str,
    control_volume_udf: str,
):
    """Calculate and set the pooling aliquots needed for pooling SMRTbell libraries."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process: Process = ctx.obj["process"]

    try:
        artifacts: List[Artifact] = get_artifacts(process=process)
        for artifact in artifacts:
            target_concentration: float = get_numeric_artifact_udf(
                artifact=artifact, udf_name=target_concentration_udf
            )
            target_volume: float = get_total_pooling_volume(
                process=process,
                artifact=artifact,
                volume_udf_name=target_volume_udf,
                nr_smrt_cells_udf=sequencing_container_udf,
            )
            # 1ul diluted control is always loaded per SMRT Cell
            control_volume: float = get_numeric_artifact_udf(
                artifact=artifact, udf_name=sequencing_container_udf
            )
            set_pooling_volumes(
                pool_artifact=artifact,
                target_volume=target_volume,
                control_volume=control_volume,
                target_concentration=target_concentration,
                size_udf=size_udf,
                input_concentration_udf=concentration_udf,
                sample_volume_udf=volume_udf,
                total_volume_udf=total_volume_udf,
                buffer_volume_udf=buffer_udf,
                control_volume_udf=control_volume_udf,
            )

        message: str = "Pooling volumes have been calculated for all artifacts!"
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
