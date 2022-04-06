from genologics.entities import Process, Processtype

from cg_lims.EPPs.arnold.sequencing import build_step_documents
from cg_lims.models.arnold.base_step import BaseStep

from tests.conftest import (
    server,
)


NOVA_SEQ_STANDARD_STEP_TYPES = {
    "bcl_conversion_and_demultiplexing",
    "define_run_format",
    "standard_make_pool_and_denature",
    "standard_prepare_for_sequencing",
}


def test_nova_seq_standard(lims):
    # GIVEN: A lims with a process: "24-308692" (Bcl Conversion & Demultiplexing (Nova Seq)).
    # Where the samples in the process has gone through the whole nova seq standard protocol:

    server("novaseq_standard")
    process = Process(lims=lims, id="24-308986")

    # WHEN running build_step_documents for the novaseq sequencing_method
    step_documents = build_step_documents(lims=lims, process=process, sequencing_method="novaseq")

    # THEN assert BaseStep documents are created and all required step types in the covid prep workflow are represented
    for document in step_documents:
        assert isinstance(document, BaseStep)
    assert {document.step_type for document in step_documents} == NOVA_SEQ_STANDARD_STEP_TYPES
