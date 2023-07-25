from genologics.entities import Artifact
from cg_lims.EPPs.udf.copy.original_well_to_sample import original_well_to_sample
from tests.conftest import server
from cg_lims.exceptions import InvalidValueError
import pytest

def test_assign_position(lims):
    # GIVEN artifacts with container, position and without parent steps.
    server("reception_control_twist")
    artifacts = [Artifact(lims=lims, id="ACC9476A2PA1")]

    # When running function orgwell_to_sample.
    original_well_to_sample(artifacts=artifacts)

    # THEN the corresponding sample will have the matching 'Original Well' and 'Original Container'.
    for artifact in artifacts:
        sample = artifact.samples[0]
        assert sample.udf["Original Well"] == artifact.location[1]
        assert sample.udf["Original Container"] == artifact.location[0].name

def test_replace(lims):
    # GIVEN artifacts with container, position and without parent steps.
    # And sample with already has assigned 'Original Well' and 'Original Container'.
    server("reception_control_twist")
    artifact = [Artifact(lims=lims, id="ACC9476A23PA1")]
    sample = artifact[0].samples[0]
    sample.udf['Original Well'] = "foo"
    sample.udf['Original Container'] = "bar"
    sample.put()

    # When running function original_well_to_sample.
    if artifact[0].location[1] != None and artifact[0].location[0].name != None:
        original_well_to_sample(artifact)
    
    # THEN the corresponding sample will have the matching 'Original Well' and 'Original Container'.
    assert sample.udf["Original Well"] == artifact[0].location[1]
    assert sample.udf["Original Container"] == artifact[0].location[0].name

def test_missing_value(lims):
    # GIVEN that is missing location udf
    server("reception_control_twist")
    artifact = [Artifact(lims=lims, id="ACC9476A3PA1")]
    
    if artifact[0].location[0] != None :
        exit()
    
    # WHEN running function original_well_to_sample
    # THEN MissingUDFsError should be triggered.
    with pytest.raises(InvalidValueError) as error_message:
            original_well_to_sample(artifact)

def test_exceptions_with_parent(lims):
    # GIVEN artifacts with parent steps.
    server("covid_prep")
    artifacts = [Artifact(lims=lims, id="2-1837696"), Artifact(lims=lims, id="2-1837697")]

    for artifact in artifacts:
        if artifact.parent_process == None:
            exit()
    
    # WHEN running function original_well_to_sample.
    # THEN InvalidValueError should be raised.
    with pytest.raises(InvalidValueError) as error_message:
        original_well_to_sample(artifacts=artifacts)

def test_exceptions_pool(lims):
    # GIVEN artifacts with multiple samples, a pool.
    server("missing_reads_pool")
    artifacts = [Artifact(lims=lims, id="2-1439512"), Artifact(lims=lims, id="2-1439513")]

    for artifact in artifacts:
        if len(artifact.samples) == 1:
            exit()
    
    # WHEN running function original_well_to_sample.
    # THEN InvalidValueError should be raised.
    with pytest.raises(InvalidValueError) as error_message:
        original_well_to_sample(artifacts=artifacts)
