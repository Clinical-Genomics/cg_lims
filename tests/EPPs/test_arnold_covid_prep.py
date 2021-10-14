from genologics.entities import Process

from cg_lims.EPPs.arnold.prep import build_step_documents
from cg_lims.models.arnold.prep.base_step import BaseStep

from tests.conftest import (
    server,
)


COVID_STEP_TYPES = {"library_prep", "reception_control", "pooling_and_cleanup"}


def test_covid_prep(lims):
    # GIVEN: A lims with a process: "24-240270" (Aggregate QC (Library Validation) (Cov)).
    # Where the samples in the process has gone through the whole covid prep workflow:

    server("covid_prep")
    process = Process(lims=lims, id="24-240270")

    # WHEN running build_step_documents for the covid prep
    step_documents = build_step_documents(lims=lims, process=process, prep_type="cov")

    # THEN assert BaseStep documents are created and all requiered step types in the covid prep workflow are represented
    for document in step_documents:
        assert isinstance(document, BaseStep)
    assert {document.step_type for document in step_documents} == COVID_STEP_TYPES
