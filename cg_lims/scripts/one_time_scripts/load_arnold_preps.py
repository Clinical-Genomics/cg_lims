import logging
from typing import List, Literal

import click
from genologics.lims import Lims, Process
import requests
from requests import Response
import json

from cg_lims import options
from cg_lims.EPPs.arnold.prep import build_step_documents
from cg_lims.models.arnold.prep.base_step import BaseStep

LOG = logging.getLogger(__name__)


@click.command()
@options.prep(help="Prep type.")
@options.process_types()
@click.pass_context
def update_arnold_preps(
    ctx, prep_type: Literal["wgs", "twist", "micro", "cov", "rna"], process_types: List[str]
):
    """For ALL preps defined by prep_type and process_types, updating ALL Step documents.
    This script should in other words be run with care."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    lims: Lims = ctx.obj["lims"]
    arnold_host: str = ctx.obj["arnold_host"]
    processes = lims.get_processes(type=process_types)
    LOG.info(f"loading {len(processes)} processes")
    for process in processes:
        try:
            all_step_documents: List[BaseStep] = build_step_documents(
                prep_type=prep_type, process=process, lims=lims
            )
            response: Response = requests.put(
                url=f"{arnold_host}/steps",
                headers={"Content-Type": "application/json"},
                data=json.dumps([doc.dict(exclude_none=True) for doc in all_step_documents]),
            )
            if not response.ok:
                LOG.error(response.text)
            else:
                LOG.info(f"process loaded: {process.id}")
        except:
            LOG.error(f"faild with process {process.id}")

    click.echo("Done. See log file for details.")
