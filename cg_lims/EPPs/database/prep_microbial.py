import logging

import click
from genologics.lims import Lims, Process

from cg_lims.exceptions import LimsError
from cg_lims.get.samples import get_process_samples
from cg_lims.models.database.microbial_prep import MicrobialPrep
from cg_lims.models.database.microbial_prep.buffer_exchange import BufferExchange
from cg_lims.models.database.microbial_prep.microbial_library_prep_nextera import (
    MicrobialLibraryPrepNextera,
)
from cg_lims.models.database.microbial_prep.normailzation_of_microbial_samples_for_sequencing import (
    NormalizationOfMicrobialSamplesForSequencing,
)
from cg_lims.models.database.microbial_prep.normalization_of_microbial_samples import (
    NormalizationOfMicrobialSamples,
)
from cg_lims.models.database.microbial_prep.post_pcr_bead_purification import (
    PostPCRBeadPurification,
)
import requests
from requests import Response
import json

LOG = logging.getLogger(__name__)


def build_microbial_document(sample_id: str, process_id: str, lims: Lims) -> MicrobialPrep:
    """Building a Prep with  document."""

    prep_document = dict(
        _id=f"{sample_id}_{process_id}",
        prep_id=f"{sample_id}_{process_id}",
        sample_id=sample_id,
    )

    microbial_workflow = [
        BufferExchange(sample_id=sample_id, lims=lims),
        MicrobialLibraryPrepNextera(sample_id=sample_id, lims=lims),
        NormalizationOfMicrobialSamplesForSequencing(sample_id=sample_id, lims=lims),
        NormalizationOfMicrobialSamples(sample_id=sample_id, lims=lims),
        PostPCRBeadPurification(sample_id=sample_id, lims=lims),
    ]

    for step in microbial_workflow:
        if step.artifact_udf_model:
            prep_document.update(step.filter_artifact_udfs_by_model())
        if step.process_udf_model:
            prep_document.update(step.filter_process_udfs_by_model())

    return MicrobialPrep(**prep_document)


@click.command()
@click.pass_context
def microbial_prep_document(ctx):
    """Creating PrepCollectionMicrobial documents in the prep collection."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process: Process = ctx.obj["process"]
    lims = ctx.obj["lims"]
    arnold_host = ctx.obj["arnold_host"]
    samples = get_process_samples(process=process)

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
