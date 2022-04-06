from genologics.entities import Process

from cg_lims.EPPs.arnold.prep import build_step_documents
from cg_lims.models.arnold.base_step import BaseStep

from tests.conftest import (
    server,
)


WGS_STEP_TYPES = {
    "reception_control",
    "end_repair",
    "fragment_dna",
    "aliquot_samples_for_covaris",
}


def test_wgs_prep(lims):
    # GIVEN: A lims with a process: "24-240276" (Aggregate QC (Library Validation)).
    # Where the samples in the process has gone through the whole wgs prep workflow:

    server("wgs_prep")
    process = Process(lims=lims, id="24-240276")

    # WHEN running build_step_documents
    step_documents = build_step_documents(lims=lims, process=process, prep_type="wgs")
    # THEN assert BaseStep documents are created and all step types in the microbial workflow are represented
    for document in step_documents:
        assert isinstance(document, BaseStep)
    assert {document.step_type for document in step_documents} == WGS_STEP_TYPES
