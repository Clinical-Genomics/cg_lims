from genologics.entities import Artifact
from cg_lims.EPPs.udf.copy.location_to_artifact import copy_location_to_artifact
from tests.conftest import server
from cg_lims.exceptions import InvalidValueError
import pytest


def test_assign_position(lims):
    # GIVEN artifacts with container, position and without parent steps.
    server("reception_control_twist")
    artifacts = [Artifact(lims=lims, id="ACC9476A2PA1"),
                 Artifact(lims=lims, id="ACC9476A23PA1")]

    # When running function copy_location_to_artifact.
    copy_location_to_artifact(artifacts=artifacts, location_udfs=["Library plate Well", "Library plate Name"])

    # THEN UDFs "Library plate Well" and "Library plate Name" will have correctly copied the location information.
    for artifact in artifacts:
        assert artifact.udf["Library plate Well"] == artifact.location[1]
        assert artifact.udf["Library plate Name"] == artifact.location[0].name


def test_replace(lims):
    # GIVEN artifacts with container, position and without parent steps.
    # And sample with already has assigned "Library plate Well", "Library plate Name".
    server("reception_control_twist")
    artifacts = [Artifact(lims=lims, id="ACC9476A2PA1"),
                 Artifact(lims=lims, id="ACC9476A23PA1")]
    for artifact in artifacts:
        artifact.udf["Library plate Well"] = "foo"
        artifact.udf["Library plate Name"] = "bar"
        artifact.put()

    # When running function copy_location_to_artifact.
    copy_location_to_artifact(artifacts=artifacts, location_udfs=["Library plate Well", "Library plate Name"])

    # THEN UDFs "Library plate Well" and "Library plate Name" will have correctly copied the location information.
    for artifact in artifacts:
        assert artifact.udf["Library plate Well"] == artifact.location[1]
        assert artifact.udf["Library plate Name"] == artifact.location[0].name


def test_missing_value(lims):
    # GIVEN a list of artifacts where one is missing location
    server("reception_control_twist")
    artifacts = [Artifact(lims=lims, id="ACC9476A2PA1"),
                 Artifact(lims=lims, id="ACC9476A3PA1"),
                 Artifact(lims=lims, id="ACC9476A23PA1")]
    
    # WHEN running function copy_location_to_artifact
    with pytest.raises(InvalidValueError) as error_message:
        copy_location_to_artifact(artifacts=artifacts, location_udfs=["Library plate Well", "Library plate Name"])

    # THEN InvalidValueError should be triggered with the correct error message
    assert (
            f"Failed to set Library plate Well and Library plate Name for 1 artifacts."
            f" UDFs were set on 2 samples."
            in error_message.value.message
    )