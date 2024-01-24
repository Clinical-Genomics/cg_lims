import logging
from typing import List

import click
import requests
from cg_lims import options
from cg_lims.EPPs.arnold.flow_cell import build_flow_cell_document
from cg_lims.get.artifacts import OutputGenerationType, OutputType, get_output_artifacts
from cg_lims.models.arnold.flow_cell import FlowCell
from genologics.lims import Lims
from requests import Response

LOG = logging.getLogger(__name__)


@click.command()
@options.process_types()
@click.pass_context
def update_arnold_flow_cells(ctx, process_types: List[str]):
    """For ALL runs defined by process_types, updating ALL Flow Cell documents.
    This script should in other words be run with care."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    lims: Lims = ctx.obj["lims"]
    arnold_host: str = ctx.obj["arnold_host"]
    processes = lims.get_processes(type=process_types)
    LOG.info(f"loading {len(processes)} processes")
    for process in processes:
        try:
            lanes = get_output_artifacts(
                process=process,
                output_generation_types=[OutputGenerationType.PER_INPUT],
                lims=lims,
                output_type=OutputType.RESULT_FILE,
            )
            flow_cell_document: FlowCell = build_flow_cell_document(process=process, lanes=lanes)
            response: Response = requests.post(
                url=f"{arnold_host}/flow_cell",
                headers={"Content-Type": "application/json"},
                data=flow_cell_document.json(exclude_none=True),
            )

            if not response.ok:
                LOG.error(response.text)
            else:
                LOG.info(f"process loaded: {process.id}")
        except:
            LOG.error(f"faild with process {process.id}")

    click.echo("Done. See log file for details.")
