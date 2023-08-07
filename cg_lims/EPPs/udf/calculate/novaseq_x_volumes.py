import logging
import sys

import click
from typing import List
from genologics.entities import Artifact, Process

from cg_lims.exceptions import LimsError, MissingUDFsError, InvalidValueError
from cg_lims.get.artifacts import get_artifacts

LOG = logging.getLogger(__name__)


FLOW_CELL_LANE_VOLUMES = {"10B": 34}
FLOW_CELL_SIZE = {"10B": 8}


def get_flow_cell_type(process: Process) -> str:
    """Return flow cell type from a process."""
    flow_cell_type: str = process.udf.get("Flow Cell Type")
    if not flow_cell_type:
        raise MissingUDFsError(
            "You need to specify a flow cell type before volumes can be calculated."
        )
    return flow_cell_type


def get_number_of_lanes(process: Process) -> int:
    """Return number of lanes to load from a process."""
    number_of_lanes: int = process.udf.get("Lanes to Load")
    if not number_of_lanes or number_of_lanes == 0:
        raise MissingUDFsError(
            "You need to specify a number of lanes to load before volumes can be calculated."
        )
    return int(number_of_lanes)


def get_final_loading_concentration(process: Process) -> float:
    """Return the final loading concentration from a process."""
    final_concentration: float = process.udf.get("Final Loading Concentration (pM)")
    if not final_concentration or final_concentration == 0:
        raise MissingUDFsError("You need to specify a final loading concentration value above 0.")
    return final_concentration


def get_minimum_sample_volume(process: Process) -> float:
    """Return the minimum per sample volume from a process."""
    min_sample_volume: float = process.udf.get("Minimum Per Sample Volume (ul)")
    if not min_sample_volume:
        raise MissingUDFsError("You need to specify a minimum per sample volume (in µl).")
    return min_sample_volume


def calculate_bulk_volume(process: Process) -> float:
    """Calculate and return bulk volume from a process."""
    flow_cell_type: str = get_flow_cell_type(process=process)
    if flow_cell_type not in FLOW_CELL_LANE_VOLUMES.keys():
        raise InvalidValueError(
            f"Flow cell type '{flow_cell_type}' not supported by current automation."
        )
    number_of_lanes: int = get_number_of_lanes(process=process)
    if number_of_lanes > FLOW_CELL_SIZE[flow_cell_type]:
        raise InvalidValueError(
            f"Number of lanes ({number_of_lanes}) can't exceed flow cell size ({FLOW_CELL_SIZE[flow_cell_type]} for {flow_cell_type})."
        )
    return number_of_lanes * FLOW_CELL_LANE_VOLUMES[flow_cell_type]


def calculate_total_reads(artifacts: List[Artifact]) -> float:
    """Calculate and return the total amount of reads to sequence from a list of artifacts."""
    total_amount: float = 0
    no_reads: int = 0
    for artifact in artifacts:
        target_reads: float = float(artifact.udf.get("Reads to sequence (M)", 0))
        if target_reads == 0:
            no_reads += 1
            LOG.info(f"Artifact {artifact.id} has no targeted reads to sequence.")
        else:
            total_amount = total_amount + target_reads
    if no_reads:
        LOG.info(f"Warning: {no_reads} sample(s)/pool(s) have no 'Reads to sequence (M)' amount.")
    return total_amount


def calculate_and_set_sample_volume(
    artifacts: List[Artifact], final_concentration: float, bulk_volume: float
) -> None:
    """Calculate and set the sample volume on artifact level."""
    total_reads: float = calculate_total_reads(artifacts=artifacts)
    if total_reads == 0:
        raise InvalidValueError("You need to specify an amount of reads to sequence larger than 0.")
    for artifact in artifacts:
        fraction_of_pool: float = float(artifact.udf.get("Reads to sequence (M)", 0)) / total_reads
        if not artifact.udf.get("Concentration (nM)"):
            raise MissingUDFsError(
                f"UDF 'Concentration (nM)' missing for artifact {artifact.name}."
            )
        sample_volume: float = fraction_of_pool * (
            ((final_concentration * (5 / 1000.0)) / float(artifact.udf["Concentration (nM)"]))
            * bulk_volume
        )
        artifact.udf["Per Sample Volume (ul)"] = sample_volume
        artifact.put()


def get_smallest_artifact_volume(artifacts: List[Artifact]) -> float:
    """Return the smallest volume from a list of artifacts."""
    min_artifact_volume = None
    for artifact in artifacts:
        artifact_volume: float = artifact.udf.get("Per Sample Volume (ul)")
        if not min_artifact_volume or min_artifact_volume > artifact_volume:
            min_artifact_volume = artifact_volume
    return min_artifact_volume


def calculate_min_volume_ratio(artifacts: List[Artifact], min_sample_volume: float) -> float:
    """Calculate and return the ratio between the smallest artifact volume and a set threshold if it is below it."""
    smallest_volume: float = get_smallest_artifact_volume(artifacts=artifacts)
    if smallest_volume and min_sample_volume > smallest_volume:
        return min_sample_volume / smallest_volume
    else:
        return 1


def calculate_and_set_adjusted_sample_volume(
    artifacts: List[Artifact], min_sample_volume: float
) -> None:
    """Calculate and set the adjusted sample volume on artifact level."""
    ratio: float = calculate_min_volume_ratio(
        artifacts=artifacts, min_sample_volume=min_sample_volume
    )
    for artifact in artifacts:
        artifact.udf["Adjusted Per Sample Volume (ul)"] = (
            artifact.udf.get("Per Sample Volume (ul)", 0) * ratio
        )
        artifact.put()


def calculate_adjusted_bulk_volume(process: Process) -> float:
    """Calculate and return the adjusted bulk volume."""
    bulk_volume: float = calculate_bulk_volume(process=process)
    ratio: float = calculate_min_volume_ratio(
        artifacts=get_artifacts(process=process),
        min_sample_volume=get_minimum_sample_volume(process=process),
    )
    return bulk_volume * ratio


def calculate_total_sample_volume(artifacts: List[Artifact]) -> float:
    """Calculate and return the total sample volume from a list of artifacts."""
    total_sample_volume: float = 0
    for artifact in artifacts:
        total_sample_volume += artifact.udf.get("Adjusted Per Sample Volume (ul)")
    return total_sample_volume


def calculate_rsb_volume(artifacts: List[Artifact], adjusted_bulk_volume: float) -> float:
    """Calculate and return the RSB volume."""
    return adjusted_bulk_volume - calculate_total_sample_volume(artifacts=artifacts)


def set_volumes_and_total_reads(process: Process) -> None:
    """Set artifact and process UDF values."""
    artifacts: List[Artifact] = get_artifacts(process=process)
    final_concentration: float = get_final_loading_concentration(process=process)
    min_sample_volume: float = get_minimum_sample_volume(process=process)
    bulk_volume: float = calculate_bulk_volume(process=process)
    total_reads: float = calculate_total_reads(artifacts=artifacts)

    calculate_and_set_sample_volume(
        artifacts=artifacts, final_concentration=final_concentration, bulk_volume=bulk_volume
    )
    adjusted_bulk_volume: float = calculate_adjusted_bulk_volume(process=process)
    calculate_and_set_adjusted_sample_volume(
        artifacts=artifacts, min_sample_volume=min_sample_volume
    )
    total_sample_volume: float = calculate_total_sample_volume(artifacts=artifacts)
    rsb_volume = calculate_rsb_volume(
        artifacts=artifacts, adjusted_bulk_volume=adjusted_bulk_volume
    )

    process.udf["Adjusted Bulk Pool Volume (ul)"] = adjusted_bulk_volume
    process.udf["Total Sample Volume (ul)"] = round(total_sample_volume, 2)
    process.udf["RSB Volume (ul)"] = round(rsb_volume, 2)
    process.udf["Total nr of Reads Requested (sum of reads to sequence)"] = total_reads
    process.put()


@click.command()
@click.pass_context
def novaseq_x_volumes(ctx):
    """Calculates and sets volumes required for preparation of NovaSeq X pools."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process: Process = ctx.obj["process"]

    try:
        set_volumes_and_total_reads(process=process)
        message: str = "NovaSeq X volumes have been calculated and set."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
