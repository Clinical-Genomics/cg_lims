import logging
from typing import List

import click
from genologics.entities import Sample
from genologics.lims import Lims

from cg_lims.adapter.plugin import get_cg_lims_adapter
from cg_lims.exeptions import InsertError
from cg_lims.get.artifacts import get_latest_artifact
from cg_lims.get.samples import get_process_samples
from cg_lims.models.database.prep import (
    MicrobialLibraryPrepNexteraProcessUDFS,
    PostPCRBeadPurificationProcessUDFS,
    PostPCRBeadPurificationArtifactUDF,
    NormalizationOfMicrobialSamplesForSequencingProcessUDFS,
    BufferExchangeProcessUDFS,
    NormalizationOfMicrobialSamplesProcessUDFS,
)
from cg_lims.models.database.prepp_ import PrepCollectionMicrobial
from cg_lims.crud.create import create_preps

LOG = logging.getLogger(__name__)


def build_document(sample: Sample, process_id: str, lims: Lims):
    """Building a PrepCollectionMicrobial document."""
    prep_dict = dict(
        _id=f"{sample.id}_{process_id}",
        prep_id=f"{sample.id}_{process_id}",
        sample_id=sample.id,
    )

    artifact = get_latest_artifact(
        lims=lims, sample_id=sample.id, process_type=["Buffer Exchange v1"]
    )
    process_udf = dict(artifact.parent_process.udf)
    BufferExchangeProcessUDFS(**process_udf)

    artifact = get_latest_artifact(
        lims=lims, sample_id=sample.id, process_type=["CG002 - Normalization of microbial samples"]
    )
    process_udf = dict(artifact.parent_process.udf)
    NormalizationOfMicrobialSamplesProcessUDFS(**process_udf)

    ## Microbial Library Prep (Nextera) v2
    artifact = get_latest_artifact(
        lims=lims, sample_id=sample.id, process_type=["Microbial Library Prep (Nextera) v2"]
    )
    process_udf = dict(artifact.parent_process.udf)
    MicrobialLibraryPrepNexteraProcessUDFS(**process_udf)

    ## "Post-PCR bead purification v1"
    artifact = get_latest_artifact(
        lims=lims, sample_id=sample.id, process_type=["Post-PCR bead purification v1"]
    )
    artifact_udf = dict(artifact.udf)
    process_udf = dict(artifact.parent_process.udf)

    PostPCRBeadPurificationProcessUDFS(**process_udf)
    PostPCRBeadPurificationArtifactUDF(**artifact_udf)

    ## CG002 - Normalization of microbial samples for sequencing
    artifact = get_latest_artifact(
        lims=lims,
        sample_id=sample.id,
        process_type=["CG002 - Normalization of microbial samples for sequencing"],
    )
    process_udf = dict(artifact.parent_process.udf)
    NormalizationOfMicrobialSamplesForSequencingProcessUDFS(**process_udf)

    return PrepCollectionMicrobial(**prep_dict)


@click.command()
@click.pass_context
def microbial_prep_document(ctx):
    """Creating PrepCollectionMicrobial documents in the prep collection."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process = ctx.obj["process"]
    lims = ctx.obj["lims"]
    adapter = get_cg_lims_adapter(db_uri=ctx.obj["db_uri"], db_name=ctx.obj["db_name"])
    samples = get_process_samples(process=process)

    try:
        prep_documents: List[PrepCollectionMicrobial] = [
            build_document(sample=sample, process_id=process.id, lims=lims) for sample in samples
        ]
        document_ids: List[str] = create_preps(adapter=adapter, preps=prep_documents)
        document_ids_str = [str(document_id) for document_id in document_ids]
        message = f"Created documents {' ,'.join(document_ids_str)} in prep collection"
        LOG.info(message)
        click.echo(message)
    except:
        raise InsertError(message="Failed to insert document.")
