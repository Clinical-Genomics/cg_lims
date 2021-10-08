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
from cg_lims.models.arnold.prep.twist import (
    get_pool_samples_twist,
    get_bead_purification_twist,
    get_buffer_exchange_twist,
    get_hybridize_library_twist,
    get_kapa_library_preparation_twist,
    get_aliquot_samples_for_enzymatic_fragmentation_udfs,
    get_capture_and_wash,
    get_pre_processing_twist,
    get_enzymatic_fragmentation,
    get_amplify_captured_library_udfs,
)

LOG = logging.getLogger(__name__)


def build_twist_document(sample_id: str, process_id: str, lims: Lims) -> List[BaseStep]:
    """Building a sars_cov_2 Prep."""
    prep_id = f"{sample_id}_{process_id}"
    return [
        get_aliquot_samples_for_enzymatic_fragmentation_udfs(
            sample_id=sample_id, lims=lims, prep_id=prep_id
        ),
        get_hybridize_library_twist(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_pool_samples_twist(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_capture_and_wash(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_kapa_library_preparation_twist(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_buffer_exchange_twist(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_bead_purification_twist(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_enzymatic_fragmentation(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_amplify_captured_library_udfs(sample_id=sample_id, lims=lims, prep_id=prep_id),
        get_pre_processing_twist(sample_id=sample_id, lims=lims, prep_id=prep_id),
    ]


@click.command()
@click.pass_context
def twist_prep_document(ctx):
    """Creating Prep documents in the arnold Prep collection."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process: Process = ctx.obj["process"]
    lims: Lims = ctx.obj["lims"]
    arnold_host: str = ctx.obj["arnold_host"]
    samples: List[Sample] = get_process_samples(process=process)

    all_step_documents = []
    for sample in samples:
        step_documents: List[BaseStep] = build_twist_document(
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
    click.echo("Twist step documents inserted to arnold database")
