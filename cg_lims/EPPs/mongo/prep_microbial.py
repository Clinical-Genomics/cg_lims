import logging
from typing import List

import click
from genologics.lims import Lims, Process

from cg_lims.exeptions import InsertError
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
)
from cg_lims.models.database.prep import Prep
import requests
from requests import Response

LOG = logging.getLogger(__name__)


def build_microbial_document(sample_id: str, process_id: str, lims: Lims):
    """Building a PrepCollectionMicrobial document."""

    prep_dict = dict(
        _id=f"{sample_id}_{process_id}",
        prep_id=f"{sample_id}_{process_id}",
        sample_id=sample_id,
        workflow="Microbial-WGS",
    )

    artifact_udfs = filter_process_artifact_udfs_by_model(
        lims=lims,
        sample_id=sample_id,
        process_type="Buffer Exchange v1",
        model=BufferExchangeArtifactUDF,
    )
    prep_dict.update(artifact_udfs)

    process_udfs = filter_process_udfs_by_model(
        lims=lims,
        sample_id=sample_id,
        process_type="Buffer Exchange v1",
        model=BufferExchangeProcessUDFS,
    )
    prep_dict.update(process_udfs)

    process_udfs = filter_process_udfs_by_model(
        lims=lims,
        sample_id=sample_id,
        process_type="CG002 - Normalization of microbial samples",
        model=NormalizationOfMicrobialSamplesProcessUDFS,
    )
    prep_dict.update(process_udfs)

    process_udfs = filter_process_udfs_by_model(
        lims=lims,
        sample_id=sample_id,
        process_type="Microbial Library Prep (Nextera) v2",
        model=MicrobialLibraryPrepNexteraProcessUDFS,
    )
    prep_dict.update(process_udfs)

    process_udfs = filter_process_udfs_by_model(
        lims=lims,
        sample_id=sample_id,
        process_type="Post-PCR bead purification v1",
        model=PostPCRBeadPurificationProcessUDFS,
    )
    prep_dict.update(process_udfs)

    artifact_udfs = filter_process_artifact_udfs_by_model(
        lims=lims,
        sample_id=sample_id,
        process_type="Post-PCR bead purification v1",
        model=PostPCRBeadPurificationArtifactUDF,
    )
    prep_dict.update(artifact_udfs)

    process_udfs = filter_process_udfs_by_model(
        lims=lims,
        sample_id=sample_id,
        process_type="CG002 - Normalization of microbial samples for sequencing",
        model=NormalizationOfMicrobialSamplesForSequencingProcessUDFS,
    )
    prep_dict.update(process_udfs)
    return PrepCollectionMicrobial(**prep_dict)


@click.command()
@click.pass_context
def microbial_prep_document(ctx):
    """Creating PrepCollectionMicrobial documents in the prep collection."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process: Process = ctx.obj["process"]
    lims = ctx.obj["lims"]
    arnold_host = ctx.obj["arnold_host"]
    samples = get_process_samples(process=process)

    try:
        prep_documents: List[Prep] = [
            build_microbial_document(sample_id=sample.id, process_id=process.id, lims=lims)
            for sample in samples
        ]

        for prep_document in prep_documents:
            response: Response = requests.post(
                url=f"{arnold_host}/insert/prep",
                headers={"Content-Type": "application/json"},
                data=prep_document.json(exclude_none=True),
            )
            if not response.ok:
                raise InsertError(response.text)
            LOG.info("Arnold output: %s", response.text)

    except:
        raise InsertError("Failed to insert docs")
