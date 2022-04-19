import logging
from typing import List

import click
from genologics.lims import Process, Lims, Artifact
import requests
from requests import Response
import json

from cg_lims.exceptions import LimsError
from cg_lims.get.artifacts import get_artifacts, get_output_artifacts

from cg_lims.models.arnold.flow_cell import Flowcell, Lane


LOG = logging.getLogger(__name__)


def build_flowcell_document(process: Process, lanes: List[Artifact]) -> Flowcell:
    flowcell = Flowcell(**dict(process.udf.items()), date=process.date_run)

    for lane in lanes:
        if not lane.location:
            continue
        flowcell.lanes.append(Lane(**dict(lane.udf.items())))

    return flowcell


@click.command()
@click.pass_context
def flowcell(ctx):
    """Creating Flowcell documents from a run in the arnold flowcell collection."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process: Process = ctx.obj["process"]
    lims: Lims = ctx.obj["lims"]
    arnold_host: str = ctx.obj["arnold_host"]
    lanes = get_output_artifacts(
        process=process, output_generation_type=["PerInput"], lims=lims, output_type="ResultFile"
    )
    flowcell_document: Flowcell = build_flowcell_document(process=process, lanes=lanes)
    response: Response = requests.post(
        url=f"{arnold_host}/flow_cell",
        headers={"Content-Type": "application/json"},
        data=flowcell_document.json(exclude_none=True),
    )
    if not response.ok:
        LOG.info(response.text)
        raise LimsError(response.text)

    LOG.info("Arnold output: %s", response.text)
    click.echo("Flowcell document inserted to arnold database")
