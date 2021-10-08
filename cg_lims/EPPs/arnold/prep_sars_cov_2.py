import logging
from typing import List

import click
from genologics.lims import Lims, Process, Sample
import requests
from requests import Response
import json
from cg_lims.exceptions import LimsError
from cg_lims.get.samples import get_process_samples
from cg_lims.models.arnold.prep.base_step import BaseStep
from cg_lims.models.arnold.prep.sars_cov_2_prep import (
    get_pooling_and_cleanup_udfs,
    get_library_prep_cov_udfs,
    get_aggregate_qc_dna_cov_udfs,
)

LOG = logging.getLogger(__name__)


def build_sars_cov_2_document(sample_id: str, process_id: str, lims: Lims) -> List[BaseStep]:
    """Building a sars_cov_2 Prep."""
    prep_id = f"{sample_id}_{process_id}"
    return [
        get_pooling_and_cleanup_udfs(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_library_prep_cov_udfs(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_aggregate_qc_dna_cov_udfs(sample_id=sample_id, lims=lims, prep_id=prep_id),
    ]


@click.command()
@click.pass_context
def sars_cov_2_prep_document(ctx):
    """Creating Prep documents in the arnold Prep collection."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process: Process = ctx.obj["process"]
    lims: Lims = ctx.obj["lims"]
    arnold_host: str = ctx.obj["arnold_host"]
    samples: List[Sample] = get_process_samples(process=process)

    all_step_documents = []
    for sample in samples:
        step_documents: List[BaseStep] = build_sars_cov_2_document(
            sample_id=sample.id, process_id=process.id, lims=lims
        )
        all_step_documents += step_documents
    response: Response = requests.post(
        url=f"{arnold_host}/steps",
        headers={"Content-Type": "application/json"},
        data=json.dumps([doc.dict(exclude_none=True) for doc in all_step_documents]),
    )
    if not response.ok:
        LOG.info(response.text)
        raise LimsError(response.text)

    LOG.info("Arnold output: %s", response.text)
    click.echo("Covid step documents inserted to arnold database")
