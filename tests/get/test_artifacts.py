from cg_lims.get.artifacts import get_latest_artifact, get_artifacts
from cg_lims.exceptions import MissingArtifactError, MissingUDFsError

import pytest


def test_get_latest_artifact(lims, sample, helpers):
    # GIVEN a lims with a sample that has been run through the same 
    # type of process twise but on two diferent dates. 
    sample_id = "SomeSampleID"
    process_type = "SomeTypeOfProcess"
    first_date = "2019-01-01"
    last_date = "2020-01-01"

    sample.id = sample_id

    helpers.ensure_lims_process(lims = lims,
        process_type_name=process_type,
        date_run=first_date,
        output_artifacts=[helpers.create_artifact(samples=[sample], type="Analyte")],
    )
    helpers.ensure_lims_process(lims = lims,
        process_type_name=process_type,
        date_run=last_date,
        output_artifacts=[helpers.create_artifact(samples=[sample], type="Analyte")],
    )

    # WHEN running get_latest_artifact with the sample id and the process type name
    latest_artifact = get_latest_artifact(
        lims=lims, sample_id=sample_id, process_type=[process_type]
    )

    # THEN the artifact from the latest process will be returned
    assert latest_artifact.parent_process.date_run == "2020-01-01"


def test_get_latest_artifact_no_artifacts(lims):
    # GIVEN a lims with no artifacts
    sample_id = ""
    process_types = []

    # WHEN running get_latest_artifact
    # THEN MissingArtifactError is raised
    with pytest.raises(MissingArtifactError):
        latest_artifact = get_latest_artifact(
            lims=lims, sample_id=sample_id, process_type=process_types
        )


def test_get_artifacts_no_output_artifacts(process):
    # GIVEN a process with no output artifacts
    # WHEN running get_artifacts
    artifacts = get_artifacts(process, input=False)

    # THEN artifacts is a empty list
    assert artifacts == []


def test_get_artifacts_with_output_artifacts(process, helpers):
    # GIVEN a process with five output artifacts
    five_artifacts = helpers.create_many_artifacts(nr_of_artifacts=5, type='Analyte')
    process.outputs = five_artifacts

    # WHEN running get_artifacts
    output_artifacts = get_artifacts(process, input=False)

    # THEN assert output_artifacts are five
    assert len(output_artifacts) == 5


def test_get_artifacts_with_input_artifacts(process, helpers):
    # GIVEN a process with five output artifacts
    five_artifacts = helpers.create_many_artifacts(nr_of_artifacts=5, type='Analyte')
    process.inputs = five_artifacts

    # WHEN running get_artifacts
    input_artifacts = get_artifacts(process, input=True)

    # THEN assert input_artifacts are five
    assert len(input_artifacts) == 5


