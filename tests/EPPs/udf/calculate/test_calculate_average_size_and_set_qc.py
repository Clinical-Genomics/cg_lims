import pytest
from genologics.entities import Artifact, Process

from cg_lims.EPPs.udf.calculate.calculate_average_size_and_set_qc import calculate_average_size, set_average_and_qc
from cg_lims.exceptions import MissingUDFsError, MissingCgFieldError
from cg_lims.set.udfs import copy_artifact_to_artifact
from tests.conftest import server


def test_calculate_average_size(lims):
    # GIVEN a list of artifacts where some have udf "size (bp)"
    # set to some integer and some are None.
    # And given that the average of the values is 244

    server("calculate_average_size_and_set_qc")
    process = Process(lims, id="24-297378")
    all_artifacts = process.all_inputs()

    # WHEN running calculate_average_size
    average = calculate_average_size(all_artifacts=all_artifacts)

    # THEN the calculated average is 244
    assert int(average) == 244


def test_calculate_average_size_no_sizes_given(lims):
    # GIVEN a list of artifacts that dont have the udf "size (bp)" set.

    server("calculate_average_size_and_set_qc")
    process = Process(lims, id="24-297378")
    all_artifacts = process.all_inputs()
    for artifact in all_artifacts:
        artifact.udf.clear()
        artifact.put()

    # WHEN running calculate_average_size
    # THEN MissingUDFsError is being raised
    with pytest.raises(MissingUDFsError) as error_message:
        average = calculate_average_size(all_artifacts=all_artifacts)


def test_calculate_average_size_ntc_only(lims):
    # Given a list of NTC artifacts that have "Size (bp)" set.

    server("calculate_average_size_and_set_qc")
    process = Process(lims, id="24-297378")
    all_artifacts = process.all_inputs()
    ntc_artifacts = [artifact for artifact in all_artifacts if artifact.name[0:3] == "NTC"]

    # WHEN running calculate_average_size
    # THEN MissingUDFsError is being raised
    with pytest.raises(MissingUDFsError) as error_message:
        average = calculate_average_size(all_artifacts=ntc_artifacts)


def test_set_average_and_qc(lims):
    # GIVEN a list of artifacts with mixed QC flags and an average of 400, which is over the lower threshold
    server("calculate_average_size_and_set_qc")
    process = Process(lims, id="24-297378")
    all_artifacts = process.all_inputs()
    all_artifacts[0].qc_flag = "FAILED"
    all_artifacts[1].qc_flag = "PASSED"

    # WHEN running set_average_and_qc
    set_average_and_qc(average=400, lower_threshold="300", upper_threshold="", all_artifacts=all_artifacts)

    # THEN the average set is 400 and the QC flags of the artifacts are unchanged if already existing,
    # or set to "PASSED" if previously set to None
    for artifact in all_artifacts:
        assert artifact.udf["Average Size (bp)"] == "400"
    assert all_artifacts[0].qc_flag == "FAILED"
    for artifact in all_artifacts[1:]:
        assert artifact.qc_flag == "PASSED"


def test_set_average_and_qc_under_lt(lims):
    # GIVEN a list of artifacts with mixed QC flags and an average of 200, which is under the lower threshold
    server("calculate_average_size_and_set_qc")
    process = Process(lims, id="24-297378")
    all_artifacts = process.all_inputs()
    all_artifacts[0].qc_flag = "FAILED"
    all_artifacts[1].qc_flag = "PASSED"

    # WHEN running set_average_and_qc
    set_average_and_qc(average=200, lower_threshold="300", upper_threshold="600", all_artifacts=all_artifacts)

    # THEN the average set is 200 and the QC flags of the artifacts are all set to "FAILED",
    # no matter what the previous state was
    for artifact in all_artifacts:
        assert artifact.udf["Average Size (bp)"] == "200"
        assert artifact.qc_flag == "FAILED"


def test_set_average_and_qc_over_ut(lims):
    # GIVEN a list of artifacts with mixed QC flags and an average of 700, which is over the upper threshold
    server("calculate_average_size_and_set_qc")
    process = Process(lims, id="24-297378")
    all_artifacts = process.all_inputs()
    all_artifacts[0].qc_flag = "FAILED"
    all_artifacts[1].qc_flag = "PASSED"

    # WHEN running set_average_and_qc
    set_average_and_qc(average=700, lower_threshold="300", upper_threshold="600", all_artifacts=all_artifacts)

    # THEN the average set is 700 and the QC flags of the artifacts are all set to "FAILED",
    # no matter what the previous state was
    for artifact in all_artifacts:
        assert artifact.udf["Average Size (bp)"] == "700"
        assert artifact.qc_flag == "FAILED"
