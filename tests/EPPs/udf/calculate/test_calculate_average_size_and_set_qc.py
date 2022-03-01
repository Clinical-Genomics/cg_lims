import pytest
from genologics.entities import Artifact, Process

from cg_lims.EPPs.udf.calculate.calculate_average_size_and_set_qc import calculate_average_size
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
