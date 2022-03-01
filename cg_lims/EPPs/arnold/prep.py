import logging
from typing import List, Literal

import click
from genologics.lims import Lims, Process, Sample
import requests
from requests import Response
import json

from cg_lims import options
from cg_lims.exceptions import LimsError
from cg_lims.get.samples import get_process_samples
from cg_lims.models.arnold.prep.base_step import BaseStep
from cg_lims.models.arnold.prep.microbial_prep import build_microbial_step_documents
from cg_lims.models.arnold.prep.wgs import build_wgs_documents
from cg_lims.models.arnold.prep.sars_cov_2_prep import build_sars_cov_2_documents
from cg_lims.models.arnold.prep.twist import build_twist_documents
from cg_lims.models.arnold.prep.rna import build_rna_documents


LOG = logging.getLogger(__name__)

prep_document_functions = {
    "wgs": build_wgs_documents,
    "twist": build_twist_documents,
    "micro": build_microbial_step_documents,
    "cov": build_sars_cov_2_documents,
    "rna": build_rna_documents,
}


def build_step_documents(
    prep_type: Literal["wgs", "twist", "micro", "cov", "rna"], process: Process, lims: Lims
) -> List[BaseStep]:
    prep_document_function = prep_document_functions[prep_type]
    samples: List[Sample] = get_process_samples(process=process)
    all_step_documents = []
    for sample in samples:
        step_documents: List[BaseStep] = prep_document_function(
            sample_id=sample.id, process_id=process.id, lims=lims
        )
        all_step_documents += step_documents
    return all_step_documents


@click.command()
@options.prep(help="Prep type.")
@click.pass_context
def prep(ctx, prep_type: Literal["wgs", "twist", "micro", "cov", "rna"]):
    """Creating Step documents from a prep in the arnold step collection."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process: Process = ctx.obj["process"]
    lims: Lims = ctx.obj["lims"]
    arnold_host: str = ctx.obj["arnold_host"]

    all_step_documents: List[BaseStep] = build_step_documents(
        prep_type=prep_type, process=process, lims=lims
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
