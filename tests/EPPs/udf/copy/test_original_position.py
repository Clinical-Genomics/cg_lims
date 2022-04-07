from genologics.entities import Artifact, Process
import click
from cg_lims.EPPs.udf.copy.orgwell_to_sample import orgwell_to_sample
from tests.conftest import server
import pytest
from cg_lims.get.artifacts import get_artifacts

def test_assign_position(ctx, lims):
    # GIVEN artifacts with container, random well position and without parent steps.
    server("reception_control_twist")
    process = ctx.obj["process"]
    process = Process(lims, id='24-315065')
    artifacts = get_artifacts(process=process, input=True)

    artifacts = [Artifact(lims=lims, id="ACC9476A2PA1"), Artifact(lims=lims, id="ACC9476A3PA1")]
    print(artifacts)

    # When running function orgwell_to_sample.
    orgwell_to_sample(artifacts=artifacts)

    # THEN the corresponding sample will have the matching 'Original Well' and 'Original Container'.
    for artifact in artifacts:
        sample = artifact.samples[0]
        print("Sample Original Well:", sample.udf['Original Well'],". Artifact:", artifact.location[1])
        assert sample.udf['Original Well'] == artifact.location[1]
        assert sample.udf['Original Container'] == artifact.location[0].name
        