from genologics.entities import Process

from cg_lims.EPPs.arnold.prep import build_step_documents
from cg_lims.models.arnold.base_step import BaseStep

from tests.conftest import (
    server,
)


MICROBIAL_STEP_TYPES = {
    "buffer_exchange",
    "reception_control",
    "normalization_for_sequencing",
    "post_pcr_bead_purification",
    "library_prep",
    "normalization",
}


def test_microbial_prep(lims):
    # GIVEN: A lims with a process: "24-240265" (CG002 - Normalization of microbial samples for sequencing).
    # Where the samples in the process has gone through the whole microbial prep workflow:

    server("microbial_prep")
    process = Process(lims=lims, id="24-240265")

    # WHEN running build_step_documents
    step_documents = build_step_documents(lims=lims, process=process, prep_type="micro")

    # THEN assert BaseStep documents are created and all step types in the microbial workflow are represented
    for document in step_documents:
        assert isinstance(document, BaseStep)
    assert {document.step_type for document in step_documents} == MICROBIAL_STEP_TYPES
