import pytest
from genologics.entities import Artifact, Process

from cg_lims.EPPs.udf.copy.artifact_to_artifact import copy_udfs_to_all_artifacts
from cg_lims.get.artifacts import get_artifacts, get_latest_analyte
from cg_lims.exceptions import MissingUDFsError
from tests.conftest import server


def test_copy_udf(lims):
    # GIVEN an Aggregate QC process with samples which have source artifacts that contain the
    # Amount (ng) UDF
    server("wgs_prep")
    process = Process(lims, id="24-240276")
    artifacts = get_artifacts(process=process, input=True)

    # WHEN running get_copy_tasks to copy the Amount (ng) UDF
    copy_udfs_to_all_artifacts(
        artifacts=artifacts,
        udfs=[("Amount (ng)", "Amount (ng)")],
        process_types=["Buffer Exchange v2"],
        lims=lims,
        sample_artifact=True,
        qc_flag=True,
        ignore_fail=False,
        keep_failed_flags=False,
    )

    # THEN the correct source UDFs are copied over
    for artifact in artifacts:
        sample_id = artifact.samples[0].id
        source_artifact = Artifact(lims, id=f"{sample_id}PA1")
        assert artifact.udf["Amount (ng)"] == source_artifact.udf["Amount (ng)"]


def test_copy_udf_process_type(lims):
    # GIVEN an Aggregate QC process with samples which have passed through an Aliquot Samples for Covaris step
    server("wgs_prep")
    process = Process(lims, id="24-240276")
    artifacts = get_artifacts(process=process, input=True)

    # WHEN running get_copy_tasks to copy the Concentration UDF
    copy_udfs_to_all_artifacts(
        artifacts=artifacts,
        udfs=[("Concentration", "Concentration")],
        process_types=["Aliquot Samples for Covaris"],
        lims=lims,
        sample_artifact=True,
        qc_flag=True,
        ignore_fail=False,
        keep_failed_flags=False,
    )

    # THEN the correct source UDFs are copied over
    for artifact in artifacts:
        sample_id = artifact.samples[0].id
        source_artifact = get_latest_analyte(lims,
                                             sample_id=sample_id,
                                             process_types=["Aliquot Samples for Covaris"],
                                             sample_artifact=False)
        assert artifact.udf["Concentration"] == source_artifact.udf["Concentration"]


def test_copy_udf_no_source(lims):
    # GIVEN an Aggregate QC process with samples which have source artifacts that doesn't contain the
    # DIN Value UDF
    server("wgs_prep")
    process = Process(lims, id="24-240276")
    artifacts = get_artifacts(process=process, input=True)

    # WHEN running get_copy_tasks
    # THEN MissingUDFError is raised
    with pytest.raises(MissingUDFsError) as error_message:
        copy_udfs_to_all_artifacts(
            artifacts=artifacts,
            udfs=[("DIN Value", "DIN Value")],
            process_types=["Buffer Exchange v2"],
            lims=lims,
            sample_artifact=True,
            qc_flag=True,
            ignore_fail=False,
            keep_failed_flags=False,
        )


def test_copy_udf_no_source_ignore(lims):
    # GIVEN an Aggregate QC process with samples which have source artifacts that doesn't contain the
    # DIN Value UDF
    server("wgs_prep")
    process = Process(lims, id="24-240276")
    artifacts = get_artifacts(process=process, input=True)

    # WHEN running get_copy_tasks with ignore_fail set to true
    # THEN no MissingUDFError is raised
    copy_udfs_to_all_artifacts(
        artifacts=artifacts,
        udfs=[("DIN Value", "DIN Value")],
        process_types=["Buffer Exchange v2"],
        lims=lims,
        sample_artifact=True,
        qc_flag=True,
        ignore_fail=True,
        keep_failed_flags=False,
    )


def test_copy_qc_flag(lims):
    # GIVEN an Aggregate QC process with samples which have source artifacts with either passing or failed qc flags
    server("wgs_prep")
    process = Process(lims, id="24-240276")
    artifacts = get_artifacts(process=process, input=True)
    source_artifact = Artifact(lims, id="ACC8454A1PA1")
    source_artifact.qc_flag = 'FAILED'
    source_artifact.put()

    # WHEN running get_copy_tasks with qc_flag set to true
    copy_udfs_to_all_artifacts(
        artifacts=artifacts,
        udfs=[],
        process_types=[],
        lims=lims,
        sample_artifact=True,
        qc_flag=True,
        ignore_fail=False,
        keep_failed_flags=False,
    )

    # THEN the correct QC flags are copied over
    for artifact in artifacts:
        sample_id = artifact.samples[0].id
        source_artifact = Artifact(lims, id=f"{sample_id}PA1")
        assert artifact.qc_flag == source_artifact.qc_flag


def test_copy_qc_flag_fail(lims):
    # GIVEN an Aggregate QC process with samples with mixed failed and passed qc flags
    server("wgs_prep")
    process = Process(lims, id="24-240276")
    artifacts = get_artifacts(process=process, input=True)
    artifacts[0].qc_flag = 'FAILED'
    artifacts[0].put()

    # WHEN running get_copy_tasks
    copy_udfs_to_all_artifacts(
        artifacts=artifacts,
        udfs=[],
        process_types=[],
        lims=lims,
        sample_artifact=True,
        qc_flag=True,
        ignore_fail=False,
        keep_failed_flags=True,
    )

    # THEN failed qc flags are not overwritten
    assert artifacts[0].qc_flag == 'FAILED'
    for artifact in artifacts[1:5]:
        sample_id = artifact.samples[0].id
        source_artifact = Artifact(lims, id=f"{sample_id}PA1")
        assert artifact.qc_flag == source_artifact.qc_flag
