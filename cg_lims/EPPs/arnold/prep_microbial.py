import logging
from typing import List

import click
from genologics.lims import Lims, Process, Sample
import requests
from requests import Response
import json
from cg_lims.exceptions import LimsError
from cg_lims.get.samples import get_process_samples
from cg_lims.models.arnold.prep.microbial_prep import (
    MicrobialPrep,
    BufferExchangeUDFS,
    get_buffer_exchange_udfs,
    get_library_prep_nextera_udfs,
    LibraryPrepUDFS,
    NormalizationOfSamplesForSequencingUDFS,
    get_normalization_of_samples_for_sequencing_udfs,
    NormalizationOfMicrobialSamplesUDFS,
    get_normalization_of_mictobial_samples_udfs,
    PostPCRBeadPurificationUDF,
    get_post_bead_pcr_purification_udfs,
)

LOG = logging.getLogger(__name__)


def build_microbial_document(sample_id: str, process_id: str, lims: Lims) -> MicrobialPrep:
    """Building a Microbial Prep."""

    library_prep_nextera_udfs: LibraryPrepUDFS = get_library_prep_nextera_udfs(
        sample_id=sample_id, lims=lims
    )

    buffer_exchange_udfs: BufferExchangeUDFS = get_buffer_exchange_udfs(
        sample_id=sample_id, lims=lims
    )
    normalization_of_samples_for_sequencing_udfs: NormalizationOfSamplesForSequencingUDFS = (
        get_normalization_of_samples_for_sequencing_udfs(sample_id=sample_id, lims=lims)
    )
    normalization_of_mictobial_samples_udfs: NormalizationOfMicrobialSamplesUDFS = (
        get_normalization_of_mictobial_samples_udfs(sample_id=sample_id, lims=lims)
    )
    post_bead_pcr_purification_udfs: PostPCRBeadPurificationUDF = (
        get_post_bead_pcr_purification_udfs(sample_id=sample_id, lims=lims)
    )

    return MicrobialPrep(
        prep_id=f"{sample_id}_{process_id}",
        sample_id=sample_id,
        **library_prep_nextera_udfs.dict(),
        **buffer_exchange_udfs.dict(),
        **normalization_of_samples_for_sequencing_udfs.dict(),
        **normalization_of_mictobial_samples_udfs.dict(),
        **post_bead_pcr_purification_udfs.dict(),
    )


@click.command()
@click.pass_context
def microbial_prep_document(ctx):
    """Creating PrepCollectionMicrobial documents in the arnold Prep collection."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process: Process = ctx.obj["process"]
    lims: Lims = ctx.obj["lims"]
    arnold_host: str = ctx.obj["arnold_host"]
    samples: List[Sample] = get_process_samples(process=process)

    prep_documents = []
    for sample in samples:
        prep_document: MicrobialPrep = build_microbial_document(
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
    click.echo("Covid prep documents inserted to arnold database")
