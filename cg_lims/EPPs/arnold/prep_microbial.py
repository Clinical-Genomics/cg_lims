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
from cg_lims.models.arnold.prep.microbial_prep import (
    get_buffer_exchange,
    get_library_prep_nextera,
    get_normalization_of_samples,
    get_normalization_of_mictobial_samples,
    get_post_bead_pcr_purification,
)

LOG = logging.getLogger(__name__)


def build_microbial_step_documents(sample_id: str, process_id: str, lims: Lims) -> List[BaseStep]:
    """Building a Step Documents for a Microbial Prep."""
    prep_id = f"{sample_id}_{process_id}"
    return [
        get_library_prep_nextera(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_buffer_exchange(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_normalization_of_samples(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_normalization_of_mictobial_samples(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_post_bead_pcr_purification(sample_id=sample_id, lims=lims, prep_id=prep_id),
    ]


@click.command()
@click.pass_context
def microbial_prep_document(ctx):
    """Creating PrepCollectionMicrobial documents in the arnold Prep collection."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process: Process = ctx.obj["process"]
    lims: Lims = ctx.obj["lims"]
    arnold_host: str = ctx.obj["arnold_host"]
    samples: List[Sample] = get_process_samples(process=process)

    all_step_documents = []
    for sample in samples:
        step_documents: List[BaseStep] = build_microbial_step_documents(
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
    click.echo("Microbial step documents inserted to arnold database")
