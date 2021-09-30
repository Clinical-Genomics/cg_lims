import logging
from typing import List

import click
from genologics.lims import Lims, Process, Sample
import requests
from requests import Response
import json
from cg_lims.exceptions import LimsError
from cg_lims.get.samples import get_process_samples
from cg_lims.models.arnold.prep.sars_cov_2_prep import (
    get_pooling_and_cleanup_udfs,
    get_library_prep_cov_udfs,
    get_aggregate_qc_dna_cov_udfs,
    LibraryPreparationCovUDFS,
    PoolingAndCleanUpCovUDF,
    AggregateQCDNACovUDF,
    SarsCov2Prep,
)

LOG = logging.getLogger(__name__)


def build_sars_cov_2_document(sample_id: str, process_id: str, lims: Lims) -> SarsCov2Prep:
    """Building a sars_cov_2 Prep."""

    pooling_and_cleanup_udfs: PoolingAndCleanUpCovUDF = get_pooling_and_cleanup_udfs(
        sample_id=sample_id, lims=lims
    )
    library_prep_cov_udfs: LibraryPreparationCovUDFS = get_library_prep_cov_udfs(
        sample_id=sample_id, lims=lims
    )
    aggregate_qc_dna_cov_udfs: AggregateQCDNACovUDF = get_aggregate_qc_dna_cov_udfs(
        sample_id=sample_id, lims=lims
    )

    return SarsCov2Prep(
        prep_id=f"{sample_id}_{process_id}",
        sample_id=sample_id,
        **pooling_and_cleanup_udfs.dict(),
        **library_prep_cov_udfs.dict(),
        **aggregate_qc_dna_cov_udfs.dict(),
    )


@click.command()
@click.pass_context
def sars_cov_2_prep_document(ctx):
    """Creating Prep documents in the arnold Prep collection."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process: Process = ctx.obj["process"]
    lims: Lims = ctx.obj["lims"]
    arnold_host: str = ctx.obj["arnold_host"]
    samples: List[Sample] = get_process_samples(process=process)

    prep_documents = []
    for sample in samples:
        prep_document: SarsCov2Prep = build_sars_cov_2_document(
            sample_id=sample.id, process_id=process.id, lims=lims
        )
        prep_documents.append(prep_document.dict(exclude_none=True))

    response: Response = requests.post(
        url=f"{arnold_host}/preps",
        headers={"Content-Type": "application/json"},
        data=json.dumps(prep_documents),
    )
    if not response.ok:
        LOG.info(response.text)
        raise LimsError(response.text)

    LOG.info("Arnold output: %s", response.text)
    click.echo("Arnold output: %s", response.text)
