import logging
from typing import List

import click
from genologics.lims import Lims, Process, Sample
import requests
from requests import Response
import json
from cg_lims.exceptions import LimsError
from cg_lims.get.samples import get_process_samples
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
    EnzymaticFragmentationTWISTUdfs,
    AmplifycapturedlibrariestwistUDFs,
    PoolsamplesforhybridizationUDFs,
    BeadPurificationUDFs,
    BufferExchangeUDFs,
    HybridizeLibraryUDFs,
    KAPALibraryPreparationUDFs,
    CaptureandWashUDFs,
    AliquotSamplesForEnzymaticFragmentationUdfs,
    TWISTPrep,
    PreProcessingUDFs,
)

LOG = logging.getLogger(__name__)


def build_twist_document(sample_id: str, process_id: str, lims: Lims) -> TWISTPrep:
    """Building a sars_cov_2 Prep."""

    aliquot_samples_for_enzymatic_fragmentation_udfs: AliquotSamplesForEnzymaticFragmentationUdfs = get_aliquot_samples_for_enzymatic_fragmentation_udfs(
        sample_id=sample_id, lims=lims
    )
    hybridize_library_twist: HybridizeLibraryUDFs = get_hybridize_library_twist(
        sample_id=sample_id, lims=lims
    )
    pool_samples_twist: PoolsamplesforhybridizationUDFs = get_pool_samples_twist(
        sample_id=sample_id, lims=lims
    )
    capture_and_wash: CaptureandWashUDFs = get_capture_and_wash(sample_id=sample_id, lims=lims)
    kapa_library_preparation_twist: KAPALibraryPreparationUDFs = get_kapa_library_preparation_twist(
        sample_id=sample_id, lims=lims
    )
    buffer_exchange_twist: BufferExchangeUDFs = get_buffer_exchange_twist(
        sample_id=sample_id, lims=lims
    )
    bead_purification_twist: BeadPurificationUDFs = get_bead_purification_twist(
        sample_id=sample_id, lims=lims
    )
    enzymatic_fragmentation: EnzymaticFragmentationTWISTUdfs = get_enzymatic_fragmentation(
        sample_id=sample_id, lims=lims
    )
    amplify_captured_library_udfs: AmplifycapturedlibrariestwistUDFs = (
        get_amplify_captured_library_udfs(sample_id=sample_id, lims=lims)
    )
    pre_processing_twist: PreProcessingUDFs = get_pre_processing_twist(
        sample_id=sample_id, lims=lims
    )
    return TWISTPrep(
        prep_id=f"{sample_id}_{process_id}",
        sample_id=sample_id,
        **bead_purification_twist.dict(),
        **buffer_exchange_twist.dict(),
        **capture_and_wash.dict(),
        **kapa_library_preparation_twist.dict(),
        **aliquot_samples_for_enzymatic_fragmentation_udfs.dict(),
        **hybridize_library_twist.dict(),
        **pool_samples_twist.dict(),
        **enzymatic_fragmentation.dict(),
        **amplify_captured_library_udfs.dict(),
        **pre_processing_twist.dict(),
    )


@click.command()
@click.pass_context
def twist_prep_document(ctx):
    """Creating Prep documents in the arnold Prep collection."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process: Process = ctx.obj["process"]
    lims: Lims = ctx.obj["lims"]
    arnold_host: str = ctx.obj["arnold_host"]
    samples: List[Sample] = get_process_samples(process=process)

    prep_documents = []
    for sample in samples:
        prep_document: TWISTPrep = build_twist_document(
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
    click.echo("Twist prep documents inserted to arnold database")
