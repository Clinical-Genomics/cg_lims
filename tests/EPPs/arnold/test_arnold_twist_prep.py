from genologics.entities import Process

from cg_lims.EPPs.arnold.prep import build_step_documents
from cg_lims.models.arnold.prep.base_step import BaseStep

from tests.conftest import (
    server,
)


TWIST_STEP_TYPES = {
    "enzymatic_fragmentation",
    "buffer_exchange",
    "kapa_library_preparation",
    "pool_samples",
    "bead_purification",
    "aliquot_samples_for_enzymatic_fragmentation",
    "hybridize_library",
    "capture_and_wash",
    "amplify_captured_library",
    "reception_control",
}


def test_twist_prep(lims):
    # GIVEN: A lims with a process: "24-240289" (Aggregate QC (Library Validation) TWIST).
    # Where the samples in the process has gone through the whole twist prep workflow:

    server("twist_prep")
    process = Process(lims=lims, id="24-240289")

    # WHEN running build_step_documents
    step_documents = build_step_documents(lims=lims, process=process, prep_type="twist")
    # THEN assert BaseStep documents are created and all step types in the twist workflow are represented
    for document in step_documents:
        assert isinstance(document, BaseStep)
    assert {document.step_type for document in step_documents} == TWIST_STEP_TYPES
