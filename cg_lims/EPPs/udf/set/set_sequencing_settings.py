import logging
import sys
import click

from typing import List, Optional
from genologics.lims import Artifact, Process
from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts

from cg_lims.EPPs.udf.calculate.constants import FlowCellTypes
from cg_lims.EPPs.udf.set.constants import DefaultReadLength, DefaultIndexLength

LOG = logging.getLogger(__name__)

DEFAULT_INDEX_LENGTHS = {
    FlowCellTypes.FLOW_CELL_10B: DefaultIndexLength.FLOW_CELL_10B,
    FlowCellTypes.FLOW_CELL_15B: DefaultIndexLength.FLOW_CELL_15B,
    FlowCellTypes.FLOW_CELL_25B: DefaultIndexLength.FLOW_CELL_25B,
}

DEFAULT_READ_LENGTHS = {
    FlowCellTypes.FLOW_CELL_10B: DefaultReadLength.FLOW_CELL_10B,
    FlowCellTypes.FLOW_CELL_15B: DefaultReadLength.FLOW_CELL_15B,
    FlowCellTypes.FLOW_CELL_25B: DefaultReadLength.FLOW_CELL_25B,
}


def get_library_tube_strip(process: Process) -> str:
    """Return the Library Tube Strip ID from a process."""
    library_tube_strip: str = process.udf.get("Library Tube Strip ID")
    if not library_tube_strip:
        LOG.error(f"Process {process.id} is missing UDF 'Library Tube Strip ID'")
        raise MissingUDFsError(f"UDF 'Library Tube Strip ID' missing from previous step.")
    return library_tube_strip


def get_flow_cell_type(process: Process) -> str:
    """Return the Flow Cell Type from a process."""
    flow_cell_type: str = process.udf.get("Flow Cell Type")
    if not flow_cell_type:
        LOG.error(f"Process {process.id} is missing UDF 'Flow Cell Type'")
        raise MissingUDFsError(f"UDF 'Flow Cell Type' missing from previous step.")
    return flow_cell_type


def set_process_udfs(process: Process, parent_process: Process) -> None:
    """Set Prepare for Sequencing (NovaSeq X) process UDFs."""
    library_tube_strip: str = get_library_tube_strip(process=parent_process)
    flow_cell_type: str = get_flow_cell_type(process=parent_process)
    process.udf["Library Tube Strip ID"] = library_tube_strip
    process.udf["Run Mode"] = flow_cell_type
    process.udf["Read 1 Cycles"] = DEFAULT_READ_LENGTHS[flow_cell_type]
    process.udf["Read 2 Cycles"] = DEFAULT_READ_LENGTHS[flow_cell_type]
    process.udf["Index Read 1"] = DEFAULT_INDEX_LENGTHS[flow_cell_type]
    process.udf["Index Read 2"] = DEFAULT_INDEX_LENGTHS[flow_cell_type]
    process.put()


def get_parent_process(process: Process) -> Optional[Process]:
    """Get the parent process of another process, assuming all input artifacts come from the same step."""
    input_artifacts: List[Artifact] = get_artifacts(process=process, input=True)
    if not input_artifacts:
        LOG.info(f"No input artifacts found for process {process.id}.")
        return None
    return input_artifacts[0].parent_process


@click.command()
@click.pass_context
def set_sequencing_settings(ctx):
    """Sets the settings required for sequencing of NovaSeq X flow cells."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process: Process = ctx.obj["process"]

    try:
        parent_process: Process = get_parent_process(process=process)
        set_process_udfs(process=process, parent_process=parent_process)
        message: str = "Sequencing settings have been successfully set."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
