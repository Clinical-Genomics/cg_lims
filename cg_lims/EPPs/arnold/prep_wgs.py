import logging
from typing import List

import click
from genologics.lims import Lims, Process, Sample
import requests
from requests import Response
import json
from cg_lims.exceptions import LimsError
from cg_lims.get.samples import get_process_samples
from cg_lims.models.arnold.prep.wgs import (
    get_end_repair_udfs,get_initial_qc_udfs,get_aliquot_samples_for_covaris_udfs,
    get_fragemnt_dna_truseq_udfs,
EndrepairSizeselectionA_tailingandAdapterligationTruSeqPCR_freeUDFS, InitialQCwgsUDF, AliquotSamplesforCovarisUDF,FragmentDNATruSeqDNAUDFS, WGSPrep
)

LOG = logging.getLogger(__name__)


def build_wgs_document(sample_id: str, process_id: str, lims: Lims) -> WGSPrep:
    """Building a sars_cov_2 Prep."""

    fragemnt_dna_truseq_udfs: FragmentDNATruSeqDNAUDFS = get_fragemnt_dna_truseq_udfs(
        sample_id=sample_id, lims=lims
    )
    initial_qc_udfs: InitialQCwgsUDF = get_initial_qc_udfs(
        sample_id=sample_id, lims=lims
    )
    aliquot_samples_for_covaris_udfs: AliquotSamplesforCovarisUDF = get_aliquot_samples_for_covaris_udfs(
        sample_id=sample_id, lims=lims
    )
    end_repair_udfs: EndrepairSizeselectionA_tailingandAdapterligationTruSeqPCR_freeUDFS = get_end_repair_udfs(
        sample_id=sample_id, lims=lims
    )
    return WGSPrep(
        prep_id=f"{sample_id}_{process_id}",
        sample_id=sample_id,
        **fragemnt_dna_truseq_udfs.dict(),
        **initial_qc_udfs.dict(),
        **aliquot_samples_for_covaris_udfs.dict(),
        **end_repair_udfs.dict(),
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
        prep_document: WGSPrep = build_wgs_document(
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
