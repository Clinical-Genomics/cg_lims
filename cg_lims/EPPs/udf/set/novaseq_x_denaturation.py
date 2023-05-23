import logging
import sys

import click
from typing import List, Optional
from genologics.entities import Artifact, Process

from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts

LOG = logging.getLogger(__name__)

DENATURATION_VOLUMES = {
    "10B": {
        "Volume of Pool to Denature (ul)": 40,
        "PhiX Volume (ul)": 1,
        "NaOH Volume (ul)": 10,
        "Pre-load Buffer Volume (ul)": 150,
    }
}

FLOW_CELL_SIZES = {"10B": 8}


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
            f"Missing number of lanes to load from previous step, using default value and assuming a fully loaded flow cell ({FLOW_CELL_SIZES[flow_cell_type]} lanes)."
        )
        return FLOW_CELL_SIZES[flow_cell_type]
    return number_of_lanes


def set_process_udfs(process: Process, parent_process: Process) -> None:
    """Set Make Pool and Denature process UDFs."""
    flow_cell_type: str = get_flow_cell_type(process=parent_process)
    number_of_lanes: int = get_number_of_lanes(process=parent_process)
    process.udf["Flow Cell Type"] = flow_cell_type
    process.udf["Lanes to Load"] = number_of_lanes
    for key, val in DENATURATION_VOLUMES[flow_cell_type].items():
        process.udf[key] = number_of_lanes * val
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
