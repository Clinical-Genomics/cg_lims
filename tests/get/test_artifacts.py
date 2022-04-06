from genologics.entities import Process
from genologics.lims import Lims
from tests.conftest import server

import pytest

from cg_lims.exceptions import MissingArtifactError
from cg_lims.get.artifacts import get_artifacts, get_latest_analyte


def test_get_latest_artifact(lims: Lims):
    # GIVEN a lims with a sample that has been run through the same
    # type of process three times but on different dates.
    server("test_get_artifacts")
    sample_id = "ACC7236A52"
    process_type = "CG002 - Sort HiSeq Samples"
    last_date = "2020-12-28"

    # WHEN running get_latest_analyte with the sample id and the process type name
    latest_artifact = get_latest_analyte(
        lims=lims, sample_id=sample_id, process_types=[process_type]
    )

    # THEN the artifact from the latest process will be returned
    assert latest_artifact.parent_process.date_run == last_date


def test_get_latest_artifact_no_artifacts(lims: Lims):
    # GIVEN a lims with no artifact related to a given sample id
    server("test_get_artifacts")
    sample_id = "SampleNotRelatedToArtifacts"
    process_type = "CG002 - Sort HiSeq Samples"

    # WHEN running get_latest_analyte
    # THEN MissingArtifactError is raised
    with pytest.raises(MissingArtifactError):
        latest_artifact = get_latest_analyte(
            lims=lims, sample_id=sample_id, process_types=process_type
        )


def test_get_artifacts_with_input_artifacts(lims: Lims):
    # GIVEN a process with one input artifacts
    server("test_get_artifacts")
    process = Process(lims, id="24-160122")
    # WHEN running get_artifacts
    input_artifacts = get_artifacts(process, input=True)

    # THEN assert input_artifacts are one
    assert len(input_artifacts) == 1


def test_get_artifacts_with_output_artifacts(lims: Lims):
    # GIVEN a process with five output artifacts
    server("test_get_artifacts")
    process = Process(lims, id="24-160122")

    # WHEN running get_artifacts
    output_artifacts = get_artifacts(process, input=False)

    # THEN assert output_artifacts are five
    assert len(output_artifacts) == 1
