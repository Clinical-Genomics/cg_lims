import pytest
from genologics.entities import Artifact, Process

from cg_lims.EPPs.udf.copy.aggregate_qc_flags_and_copy_fields import get_copy_tasks, copy_udfs
from cg_lims.get.artifacts import get_artifacts
from cg_lims.exceptions import MissingUDFsError
from tests.conftest import server


def test_get_copy_tasks_3_tasks(lims):
    # GIVEN a process with 3 copy task udfs:
    # Copy task 1 - Source Field -> Size (bp)
    # Copy task 1 - Source Step -> Tapestation QC TWIST v2
    # Copy task 2 - Source Field -> Concentration
    # Copy task 2 - Source Step -> Qubit QC (Library Validation) v2
    # Copy task 3 - Source Field -> Amount (ng)
    # Copy task 3 - Source Step -> Qubit QC (Library Validation) v2
    server("aggregate_qc")
    process = Process(lims, id="24-306120")

    # WHEN running get_copy_tasks
    source_udfs = get_copy_tasks(process=process)

    # THEN the correct source udfs are collected
    correct_source_udfs = {
        "Copy task 1": {"Source Field": "Size (bp)", "Source Step": "Tapestation QC TWIST v2"},
        "Copy task 2": {
            "Source Field": "Concentration",
            "Source Step": "Quantit QC (Library Validation) TWIST v2",
        },
        "Copy task 3": {
            "Source Field": "Amount (ng)",
            "Source Step": "Quantit QC (Library Validation) TWIST v2",
        },
    }
    assert source_udfs == correct_source_udfs


def test_get_copy_tasks_2_tasks(lims):
    # GIVEN a process with 2 copy task udfs:
    # Copy task 1 - Source Field -> Concentration (nM)
    # Copy task 1 - Source Step -> CG002 - qPCR QC (Library Validation)
    # Copy task 2 - Source Field -> Size (bp)
    # Copy task 2 - Source Step -> CG002 - qPCR QC (Library Validation)
    server("wgs_prep")
    process = Process(lims, id="24-240276")

    # WHEN running get_copy_tasks
    source_udfs = get_copy_tasks(process=process)

    # THEN the correct source udfs are collected
    correct_source_udfs = {
        "Copy task 1": {
            "Source Field": "Concentration (nM)",
            "Source Step": "CG002 - qPCR QC (Library Validation)",
        },
        "Copy task 2": {
            "Source Field": "Size (bp)",
            "Source Step": "CG002 - qPCR QC (Library Validation)",
        },
    }
    assert source_udfs == correct_source_udfs


def test_get_copy_tasks_no_tasks(lims):
    # GIVEN a process with no copy task udfs
    server("wgs_prep")
    process = Process(lims, id="24-240274")

    # WHEN running get_copy_tasks
    # THEN MissingUDFsError is raised
    with pytest.raises(MissingUDFsError) as error_message:
        source_udfs = get_copy_tasks(process=process)


def test_get_copy_tasks_wrong_type(lims):
    # GIVEN a process with no copy task udfs
    server("wgs_prep")
    process = Process(lims, id="24-240274")
    process.udf["Copy task 1 - Source Well"] = "1:1"

    # WHEN running get_copy_tasks
    # THEN MissingUDFsError is raised
    with pytest.raises(MissingUDFsError) as error_message:
        source_udfs = get_copy_tasks(process=process)
