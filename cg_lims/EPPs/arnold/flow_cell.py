import logging
from typing import List

import click
from genologics.lims import Process, Lims, Artifact
import requests
from requests import Response

from cg_lims.exceptions import LimsError
from cg_lims.get.artifacts import get_output_artifacts

from cg_lims.models.arnold.flow_cell import FlowCell, Lane


LOG = logging.getLogger(__name__)


def build_flow_cell_document(process: Process, lanes: List[Artifact]) -> FlowCell:
    flowcell = FlowCell(**dict(process.udf.items()), date=process.date_run)

    for lane in lanes:
        if not lane.location:
            continue
        flowcell.lanes.append(Lane(name=lane.name, **dict(lane.udf.items())))

    return flowcell


@click.command()
@click.pass_context
def flow_cell(ctx):
    """Creating FlowCell documents from a run in the arnold flow_cell collection."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process: Process = ctx.obj["process"]
    lims: Lims = ctx.obj["lims"]
    arnold_host: str = ctx.obj["arnold_host"]
    lanes = get_output_artifacts(
        process=process, output_generation_type=["PerInput"], lims=lims, output_type="ResultFile"
    )
    flow_cell_document: FlowCell = build_flow_cell_document(process=process, lanes=lanes)
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
