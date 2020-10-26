from cg_lims.get.artifacts import get_latest_artifact
from cg_lims.exceptions import MissingArtifactError, MissingUDFsError

import pytest



def test_get_latest_artifact(lims_with_data):
    # GIVEN a lims with no artifacts
    sample_id = 'some_sample_id'
    process_types = ['SomeTypeOfProcess']

    # WHEN running get_latest_artifact
    latest_artifact = get_latest_artifact(lims=lims_with_data, sample_id=sample_id, process_type=process_types)

    # THEN the latest artifact is returned
    assert latest_artifact.parent_process.date_run=='2020-01-01'



def test_get_latest_artifact_no_artifacts(lims):
    # GIVEN a lims with no artifacts
    sample_id = ''
    process_types = []

    # WHEN running get_latest_artifact
    # THEN MissingArtifactError is raised
    with pytest.raises(MissingArtifactError):
        latest_artifact = get_latest_artifact(lims=lims, sample_id=sample_id, process_type=process_types)


