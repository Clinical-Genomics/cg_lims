import logging
from typing import List

import click
from genologics.lims import Process, Lims, Artifact
import requests
from requests import Response

from cg_lims import options
from cg_lims.exceptions import LimsError
from cg_lims.get.artifacts import OutputGenerationType, OutputType, get_output_artifacts

from cg_lims.models.arnold.flow_cell import NovaSeq6000FlowCell, NovaSeqXFlowCell, Lane


LOG = logging.getLogger(__name__)


def build_novaseq_6000_document(process: Process, lanes: List[Artifact]) -> NovaSeq6000FlowCell:
    flowcell = NovaSeq6000FlowCell(**dict(process.udf.items()), date=process.date_run)

    for lane in lanes:
        if not lane.location:
            continue
        flowcell.lanes.append(Lane(name=lane.name, **dict(lane.udf.items())))

    return flowcell


def build_novaseq_x_document(process: Process, lanes: List[Artifact]) -> NovaSeqXFlowCell:
    flowcell = NovaSeqXFlowCell(**dict(process.udf.items()), date=process.date_run)

    for lane in lanes:
        if not lane.location:
            continue
        flowcell.lanes.append(Lane(name=lane.name, **dict(lane.udf.items())))

    return flowcell


@click.command()
@options.novaseq_x_flow_cell()
@click.pass_context
def flow_cell(ctx, novaseq_x_flow_cell: bool):
    """Creating flow cell documents from a run in the arnold flow_cell collection."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process: Process = ctx.obj["process"]
    lims: Lims = ctx.obj["lims"]
    arnold_host: str = ctx.obj["arnold_host"]
    lanes = get_output_artifacts(
        process=process,
        output_generation_types=[OutputGenerationType.PER_INPUT],
        lims=lims,
        output_type=OutputType.RESULT_FILE,
    )
    if novaseq_x_flow_cell:
        flow_cell_document: NovaSeqXFlowCell = build_novaseq_x_document(
            process=process, lanes=lanes
        )
    else:
        flow_cell_document: NovaSeq6000FlowCell = build_novaseq_6000_document(
            process=process, lanes=lanes
        )
    response: Response = requests.post(
        url=f"{arnold_host}/flow_cell",
        headers={"Content-Type": "application/json"},
        data=flow_cell_document.json(exclude_none=True),
    )
    if not response.ok:
        LOG.info(response.text)
        raise LimsError(response.text)

    LOG.info("Arnold output: %s", response.text)
    click.echo("FlowCell document inserted to arnold database")
