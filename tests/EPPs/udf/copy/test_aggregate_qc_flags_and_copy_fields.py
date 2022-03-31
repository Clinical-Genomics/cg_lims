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
        'Copy task 1':
            {'Source Field': 'Size (bp)',
             'Source Step': 'Tapestation QC TWIST v2'},
        'Copy task 2':
            {'Source Field': 'Concentration',
             'Source Step': 'Quantit QC (Library Validation) TWIST v2'},
        'Copy task 3':
            {'Source Field': 'Amount (ng)',
             'Source Step': 'Quantit QC (Library Validation) TWIST v2'}
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
        'Copy task 1':
            {'Source Field': 'Concentration (nM)',
             'Source Step': 'CG002 - qPCR QC (Library Validation)'},
        'Copy task 2':
            {'Source Field': 'Size (bp)',
             'Source Step': 'CG002 - qPCR QC (Library Validation)'}
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
    process.udf['Copy task 1 - Source Well'] = "1:1"

    # WHEN running get_copy_tasks
    # THEN MissingUDFsError is raised
    with pytest.raises(MissingUDFsError) as error_message:
        source_udfs = get_copy_tasks(process=process)


def test_copy_udfs_pools(lims):
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
    artifacts = get_artifacts(process=process, input=True)

    # WHEN running get_copy_tasks and copy_udfs
    copy_tasks = get_copy_tasks(process=process)
    copy_udfs(input_artifacts=artifacts, copy_tasks=copy_tasks, lims=lims)

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


def test_copy_udfs(lims):
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

    # WHEN running get_copy_tasks and copy_udfs
    copy_tasks = get_copy_tasks(process=process)
    copy_udfs(input_artifacts=[artifact_1, artifact_2], copy_tasks=copy_tasks, lims=lims)

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


def test_copy_udfs_qc_fail(lims):
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

    # WHEN running get_copy_tasks and copy_udfs
    copy_tasks = get_copy_tasks(process=process)
    copy_udfs(input_artifacts=[artifact_1, artifact_2], copy_tasks=copy_tasks, lims=lims)

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
