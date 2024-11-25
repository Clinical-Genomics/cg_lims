import logging
import sys
from typing import List, Optional

import click
from cg_lims.EPPs.udf.calculate.constants import (
    FlowCellLaneVolumes10B,
    FlowCellLaneVolumes15B,
    FlowCellLaneVolumes25B,
    FlowCellSize,
    FlowCellTypes,
)
from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts
from genologics.entities import Artifact, Process

LOG = logging.getLogger(__name__)


class DenaturationReagent:
    def __init__(self, per_lane_udf: str, total_udf: str, volume: float):
        self.per_lane_udf: str = per_lane_udf
        self.total_udf: str = total_udf
        self.volume: float = volume


class NovaSeqXDenaturation:
    def __init__(self, pool: float, denaturation: float, phix: float, naoh: float, buffer: float):
        self.pool: DenaturationReagent = DenaturationReagent(
            per_lane_udf="Per Lane Volume Total (ul)",
            total_udf="Total Volume of Pool to Denature (ul)",
            volume=pool,
        )
        self.denaturation: DenaturationReagent = DenaturationReagent(
            per_lane_udf="Volume of Pool to Denature (ul) per Lane",
            total_udf="Total Volume Denaturation (ul)",
            volume=denaturation,
        )
        self.phix: DenaturationReagent = DenaturationReagent(
            per_lane_udf="PhiX Volume (ul) per Lane",
            total_udf="Total PhiX Volume (ul)",
            volume=phix,
        )
        self.naoh: DenaturationReagent = DenaturationReagent(
            per_lane_udf="NaOH Volume (ul) per Lane",
            total_udf="Total NaOH Volume (ul)",
            volume=naoh,
        )
        self.buffer: DenaturationReagent = DenaturationReagent(
            per_lane_udf="Pre-load Buffer Volume (ul) per Lane",
            total_udf="Total Pre-load Buffer Volume (ul)",
            volume=buffer,
        )

    def get_reagent_list(self):
        return [self.pool, self.denaturation, self.phix, self.naoh, self.buffer]


DENATURATION_VOLUMES = {
    FlowCellTypes.FLOW_CELL_10B: NovaSeqXDenaturation(
        pool=FlowCellLaneVolumes10B.POOL_VOLUME,
        denaturation=FlowCellLaneVolumes10B.DENATURATION_VOLUME,
        phix=FlowCellLaneVolumes10B.PHIX_VOLUME,
        naoh=FlowCellLaneVolumes10B.NAOH_VOLUME,
        buffer=FlowCellLaneVolumes10B.BUFFER_VOLUME,
    ),
    FlowCellTypes.FLOW_CELL_15B: NovaSeqXDenaturation(
        pool=FlowCellLaneVolumes15B.POOL_VOLUME,
        denaturation=FlowCellLaneVolumes15B.DENATURATION_VOLUME,
        phix=FlowCellLaneVolumes15B.PHIX_VOLUME,
        naoh=FlowCellLaneVolumes15B.NAOH_VOLUME,
        buffer=FlowCellLaneVolumes15B.BUFFER_VOLUME,
    ),
    FlowCellTypes.FLOW_CELL_25B: NovaSeqXDenaturation(
        pool=FlowCellLaneVolumes25B.POOL_VOLUME,
        denaturation=FlowCellLaneVolumes25B.DENATURATION_VOLUME,
        phix=FlowCellLaneVolumes25B.PHIX_VOLUME,
        naoh=FlowCellLaneVolumes25B.NAOH_VOLUME,
        buffer=FlowCellLaneVolumes25B.BUFFER_VOLUME,
    ),
}

FLOW_CELL_SIZE = {
    FlowCellTypes.FLOW_CELL_10B: FlowCellSize.FLOW_CELL_10B,
    FlowCellTypes.FLOW_CELL_15B: FlowCellSize.FLOW_CELL_15B,
    FlowCellTypes.FLOW_CELL_25B: FlowCellSize.FLOW_CELL_25B,
}


def get_flow_cell_type(process: Process) -> str:
    """Return the Flow Cell Type from a process."""
    flow_cell_type: str = process.udf.get("Flow Cell Type")
    if not flow_cell_type:
        LOG.error(f"Process {process.id} is missing UDF 'Flow Cell Type'")
        raise MissingUDFsError(f"UDF 'Flow Cell Type' missing from previous step.")
    return flow_cell_type


def get_number_of_lanes(process: Process) -> int:
    """Return the number of Lanes to Load from a process. Requires flow cell type to be known."""
    number_of_lanes: int = process.udf.get("Lanes to Load")
    flow_cell_type: str = get_flow_cell_type(process=process)
    if not number_of_lanes:
        LOG.info(
            f"Missing number of lanes to load from previous step, "
            f"using default value and assuming a fully loaded flow cell ({FLOW_CELL_SIZE[flow_cell_type]} lanes)."
        )
        return FLOW_CELL_SIZE[flow_cell_type]
    return number_of_lanes


def set_process_udfs(process: Process, parent_process: Process) -> None:
    """Set Make Pool and Denature process UDFs."""
    flow_cell_type: str = get_flow_cell_type(process=parent_process)
    number_of_lanes: int = get_number_of_lanes(process=parent_process)
    process.udf["Flow Cell Type"] = flow_cell_type
    process.udf["Lanes to Load"] = number_of_lanes
    for reagent in DENATURATION_VOLUMES[flow_cell_type].get_reagent_list():
        process.udf[reagent.total_udf] = number_of_lanes * reagent.volume.value
        process.udf[reagent.per_lane_udf] = reagent.volume.value
    process.put()


def set_artifact_udfs(process: Process, parent_process: Process) -> None:
    """Set Make Pool and Denature artifact UDFs."""
    artifacts: List[Artifact] = get_artifacts(process=process)
    for artifact in artifacts:
        artifact.udf["Flowcell Type"] = get_flow_cell_type(process=parent_process)
        artifact.udf["Lanes to Load"] = get_number_of_lanes(process=parent_process)
        artifact.put()


def get_parent_process(process: Process) -> Optional[Process]:
    """Get the parent process of another process, assuming all input artifacts come from the same step."""
    input_artifacts: List[Artifact] = get_artifacts(process=process, input=True)
    if not input_artifacts:
        LOG.info(f"No input artifacts found for process {process.id}.")
        return None
    return input_artifacts[0].parent_process


@click.command()
@click.pass_context
def novaseq_x_denaturation(ctx):
    """Sets the volumes required for denaturation of NovaSeq X pools."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process: Process = ctx.obj["process"]

    try:
        parent_process: Process = get_parent_process(process=process)
        set_process_udfs(process=process, parent_process=parent_process)
        set_artifact_udfs(process=process, parent_process=parent_process)
        message: str = "Denaturation volumes have been calculated and set."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
