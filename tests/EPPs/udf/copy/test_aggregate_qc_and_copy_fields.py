import pytest
from genologics.entities import Artifact, Process

from cg_lims.EPPs.udf.copy.aggregate_qc_and_copy_fields import get_source_udf, copy_source_udfs_to_artifacts
from cg_lims.exceptions import MissingUDFsError
from tests.conftest import server


def test_get_source_udf_3_tasks(lims):
    # GIVEN a process with 3 copy task udfs:
    # Copy task 1 - Source Field -> Size (bp)
    # Copy task 1 - Source Step -> Tapestation QC TWIST v2
    # Copy task 2 - Source Field -> Concentration
    # Copy task 2 - Source Step -> Qubit QC (Library Validation) v2
    # Copy task 3 - Source Field -> Amount (ng)
    # Copy task 3 - Source Step -> Qubit QC (Library Validation) v2
    server("twist_prep")
    process = Process(lims, id="24-240289")

    # WHEN running get_source_udf
    source_udfs = get_source_udf(process=process)

    # THEN the correct source udfs are collected in a list of tuples
    correct_source_udfs = [
        ("Tapestation QC TWIST v2", "Size (bp)"),
        ("Qubit QC (Library Validation) v2", "Concentration"),
        ("Qubit QC (Library Validation) v2", "Amount (ng)")
    ]
    assert source_udfs == correct_source_udfs


def test_get_source_udf_2_tasks(lims):
    # GIVEN a process with 2 copy task udfs:
    # Copy task 1 - Source Field -> Concentration (nM)
    # Copy task 1 - Source Step -> CG002 - qPCR QC (Library Validation)
    # Copy task 2 - Source Field -> Size (bp)
    # Copy task 2 - Source Step -> CG002 - qPCR QC (Library Validation)
    server("wgs_prep")
    process = Process(lims, id="24-240276")

    # WHEN running get_source_udf
    source_udfs = get_source_udf(process=process)

    # THEN the correct source udfs are collected in a list of tuples
    correct_source_udfs = [
        ("CG002 - qPCR QC (Library Validation)", "Concentration (nM)"),
        ("CG002 - qPCR QC (Library Validation)", "Size (bp)")
    ]
    assert source_udfs == correct_source_udfs


def test_get_source_udf_no_tasks(lims):
    # GIVEN a process with no copy task udfs
    server("wgs_prep")
    process = Process(lims, id="24-240274")

    # WHEN running get_source_udf
    # THEN MissingUDFsError is raised
    with pytest.raises(MissingUDFsError) as error_message:
        source_udfs = get_source_udf(process=process)


def test_copy_source_udfs_to_artifacts_pools(lims):
    # GIVEN a process with 3 copy task udfs:
    # Copy task 1 - Source Field -> Size (bp)
    # Copy task 1 - Source Step -> Tapestation QC TWIST v2
    # Copy task 2 - Source Field -> Concentration
    # Copy task 2 - Source Step -> Qubit QC (Library Validation) v2
    # Copy task 3 - Source Field -> Amount (ng)
    # Copy task 3 - Source Step -> Qubit QC (Library Validation) v2
    #
    # And 2 artifacts which have gone through the necessary QC steps.

    server("aggregate_qc")
    process = Process(lims, id="24-306116")
    artifact_1 = Artifact(lims, id="2-2392049")
    artifact_2 = Artifact(lims, id="2-2392301")
    artifact_2.qc_flag = "UNKNOWN"
    artifact_2.put()

    # WHEN running copy_source_udfs_to_artifacts
    copy_source_udfs_to_artifacts(process=process, lims=lims)

    # THEN the correct values has been copied over
    correct_udfs_1 = {"Size (bp)": 450,
                      "Concentration": 1.555,
                      "Amount (ng)": 46.65}
    correct_udfs_2 = {"Size (bp)": 455,
                      "Concentration": 1.777,
                      "Amount (ng)": 53.31}
    for udf in correct_udfs_1:
        assert artifact_1.udf[udf] == correct_udfs_1[udf]
        assert artifact_2.udf[udf] == correct_udfs_2[udf]
    assert artifact_1.qc_flag == "PASSED"
    assert artifact_2.qc_flag == "PASSED"


def test_copy_source_udfs_to_artifacts(lims):
    # GIVEN a process with 3 copy task udfs:
    # Copy task 1 - Source Field -> Size (bp)
    # Copy task 1 - Source Step -> Tapestation QC TWIST v2
    # Copy task 2 - Source Field -> Concentration
    # Copy task 2 - Source Step -> Quantit QC (Library Validation) TWIST v2
    # Copy task 3 - Source Field -> Amount (ng)
    # Copy task 3 - Source Step -> Quantit QC (Library Validation) TWIST v2
    #
    # And 2 artifacts which have gone through the necessary QC steps.

    server("aggregate_qc")
    process = Process(lims, id="24-306120")
    artifact_1 = Artifact(lims, id="2-2406340")
    artifact_2 = Artifact(lims, id="2-2406348")
    artifact_2.qc_flag = "UNKNOWN"
    artifact_2.put()

    # WHEN running copy_source_udfs_to_artifacts
    copy_source_udfs_to_artifacts(process=process, lims=lims)

    # THEN the correct values has been copied over
    correct_udfs_1 = {"Size (bp)": 337,
                      "Concentration": 1.2121,
                      "Amount (ng)": 36.363}
    correct_udfs_2 = {"Size (bp)": 288,
                      "Concentration": 1.8,
                      "Amount (ng)": 54}
    for udf in correct_udfs_1:
        assert artifact_1.udf[udf] == correct_udfs_1[udf]
        assert artifact_2.udf[udf] == correct_udfs_2[udf]
    assert artifact_1.qc_flag == "PASSED"
    assert artifact_2.qc_flag == "PASSED"


def test_copy_source_udfs_to_artifacts_qc_fail(lims):
    # GIVEN a process with 3 copy task udfs:
    # Copy task 1 - Source Field -> Size (bp)
    # Copy task 1 - Source Step -> Tapestation QC TWIST v2
    # Copy task 2 - Source Field -> Concentration
    # Copy task 2 - Source Step -> Qubit QC (Library Validation) v2
    # Copy task 3 - Source Field -> Amount (ng)
    # Copy task 3 - Source Step -> Qubit QC (Library Validation) v2
    #
    # And 2 artifacts which have gone through the necessary QC steps,
    # where one failed in one of the QC steps and the other was set to
    # failed in the aggregate step.

    server("aggregate_qc")
    process = Process(lims, id="24-306116")
    artifact_1 = Artifact(lims, id="2-2392049")
    artifact_2 = Artifact(lims, id="2-2392301")
    artifact_2.qc_flag = "FAILED"
    artifact_2.put()
    tapestation = Artifact(lims, id="92-2407146")
    tapestation.qc_flag = "FAILED"
    tapestation.put()

    # WHEN running copy_source_udfs_to_artifacts
    copy_source_udfs_to_artifacts(process=process, lims=lims)

    # THEN the correct values has been copied over and both QC flags are set to FAILED
    correct_udfs_1 = {"Size (bp)": 450,
                      "Concentration": 1.555,
                      "Amount (ng)": 46.65}
    correct_udfs_2 = {"Size (bp)": 455,
                      "Concentration": 1.777,
                      "Amount (ng)": 53.31}
    for udf in correct_udfs_1:
        assert artifact_1.udf[udf] == correct_udfs_1[udf]
        assert artifact_2.udf[udf] == correct_udfs_2[udf]
    assert artifact_1.qc_flag == "FAILED"
    assert artifact_2.qc_flag == "FAILED"
