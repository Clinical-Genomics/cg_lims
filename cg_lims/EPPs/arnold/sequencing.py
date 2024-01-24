import json
import logging
from typing import List, Literal

import click
import requests
from cg_lims import options
from cg_lims.exceptions import LimsError
from cg_lims.get.samples import get_process_samples
from cg_lims.models.arnold.base_step import BaseStep
from cg_lims.models.arnold.sequencing.novaseq_6000 import build_novaseq_6000_step_documents
from cg_lims.models.arnold.sequencing.novaseq_x import build_novaseq_x_step_documents
from genologics.lims import Lims, Process, Sample
from requests import Response

LOG = logging.getLogger(__name__)

sequencing_document_functions = {
    "novaseq-6000": build_novaseq_6000_step_documents,
    "novaseq-x": build_novaseq_x_step_documents,
}


def build_step_documents(
    sequencing_method: Literal["novaseq-6000", "novaseq-x"], process: Process, lims: Lims
) -> List[BaseStep]:
    sequencing_document_function = sequencing_document_functions[sequencing_method]
    samples: List[Sample] = get_process_samples(process=process)
    all_step_documents = []
    for sample in samples:
        step_documents: List[BaseStep] = sequencing_document_function(
            sample_id=sample.id, process_id=process.id, lims=lims
        )
        all_step_documents += step_documents
    return all_step_documents


@click.command()
@options.sequencing_method(help="Sequencing Method.")
@click.pass_context
def sequencing(ctx, sequencing_method: Literal["novaseq-6000", "novaseq-x"]):
    """Creating Step documents from a run in the arnold step collection."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process: Process = ctx.obj["process"]
    lims: Lims = ctx.obj["lims"]
    arnold_host: str = ctx.obj["arnold_host"]

    all_step_documents: List[BaseStep] = build_step_documents(
        sequencing_method=sequencing_method, process=process, lims=lims
    )
    response: Response = requests.post(
        url=f"{arnold_host}/steps",
        headers={"Content-Type": "application/json"},
        data=json.dumps([doc.dict(exclude_none=True) for doc in all_step_documents]),
    )
    if not response.ok:
        LOG.info(response.text)
        raise LimsError(response.text)

    LOG.info("Arnold output: %s", response.text)
    click.echo("Step documents inserted to arnold database")
