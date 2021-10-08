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
from cg_lims.models.arnold.prep.wgs import (
    get_end_repair_udfs,
    get_initial_qc_udfs,
    get_aliquot_samples_for_covaris_udfs,
    get_fragemnt_dna_truseq_udfs,
)

LOG = logging.getLogger(__name__)


def build_wgs_document(sample_id: str, process_id: str, lims: Lims) -> List[BaseStep]:
    """Building a sars_cov_2 Prep."""

    return [
        get_fragemnt_dna_truseq_udfs(sample_id=sample_id, lims=lims),
        get_initial_qc_udfs(sample_id=sample_id, lims=lims),
        get_aliquot_samples_for_covaris_udfs(sample_id=sample_id, lims=lims),
        get_end_repair_udfs(sample_id=sample_id, lims=lims),
    ]


@click.command()
@click.pass_context
def wgs_prep_document(ctx):
    """Creating Prep documents in the arnold Prep collection."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process: Process = ctx.obj["process"]
    lims: Lims = ctx.obj["lims"]
    arnold_host: str = ctx.obj["arnold_host"]
    samples: List[Sample] = get_process_samples(process=process)

    all_step_documents = []
    for sample in samples:
        step_documents: List[BaseStep] = build_wgs_document(
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
    click.echo("WGS step documents inserted to arnold database")
