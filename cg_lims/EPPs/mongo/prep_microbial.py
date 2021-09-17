import logging
from typing import List

import click
from genologics.lims import Lims, Process

from cg_lims.exeptions import InsertError, CgLimsError
from cg_lims.get.samples import get_process_samples
from cg_lims.get.udfs import filter_process_udfs_by_model, filter_process_artifact_udfs_by_model
from cg_lims.models.database.prep.microbial_prep import (
    MicrobialLibraryPrepNexteraProcessUDFS,
    PostPCRBeadPurificationProcessUDFS,
    PostPCRBeadPurificationArtifactUDF,
    NormalizationOfMicrobialSamplesForSequencingProcessUDFS,
    BufferExchangeProcessUDFS,
    NormalizationOfMicrobialSamplesProcessUDFS,
    BufferExchangeArtifactUDF,
    MicrobialPrep,
)
from cg_lims.models.database.prep import Prep
import requests
from requests import Response
import json

LOG = logging.getLogger(__name__)


def build_microbial_document(sample_id: str, process_id: str, lims: Lims) -> Prep:
    """Building a Prep with  document."""

    prep_document = dict(
        _id=f"{sample_id}_{process_id}",
        prep_id=f"{sample_id}_{process_id}",
        sample_id=sample_id,
    )

    artifact_udfs: dict = filter_process_artifact_udfs_by_model(
        lims=lims,
        sample_id=sample_id,
        process_type="Buffer Exchange v1",
        model=BufferExchangeArtifactUDF,
    )
    prep_document.update(artifact_udfs)

    process_udfs: dict = filter_process_udfs_by_model(
        lims=lims,
        sample_id=sample_id,
        process_type="Buffer Exchange v1",
        model=BufferExchangeProcessUDFS,
    )
    prep_document.update(process_udfs)

    process_udfs: dict = filter_process_udfs_by_model(
        lims=lims,
        sample_id=sample_id,
        process_type="CG002 - Normalization of microbial samples",
        model=NormalizationOfMicrobialSamplesProcessUDFS,
    )
    prep_document.update(process_udfs)

    process_udfs: dict = filter_process_udfs_by_model(
        lims=lims,
        sample_id=sample_id,
        process_type="CG002 - Microbial Library Prep (Nextera)",
        model=MicrobialLibraryPrepNexteraProcessUDFS,
    )
    prep_document.update(process_udfs)

    process_udfs: dict = filter_process_udfs_by_model(
        lims=lims,
        sample_id=sample_id,
        process_type="Post-PCR bead purification v1",
        model=PostPCRBeadPurificationProcessUDFS,
    )
    prep_document.update(process_udfs)

    artifact_udfs: dict = filter_process_artifact_udfs_by_model(
        lims=lims,
        sample_id=sample_id,
        process_type="Post-PCR bead purification v1",
        model=PostPCRBeadPurificationArtifactUDF,
    )
    prep_document.update(artifact_udfs)

    process_udfs = filter_process_udfs_by_model(
        lims=lims,
        sample_id=sample_id,
        process_type="CG002 - Normalization of microbial samples for sequencing",
        model=NormalizationOfMicrobialSamplesForSequencingProcessUDFS,
    )
    prep_document.update(process_udfs)
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
        prep_document: Prep = build_microbial_document(
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
        raise CgLimsError(response.text)

    LOG.info("Arnold output: %s", response.text)
