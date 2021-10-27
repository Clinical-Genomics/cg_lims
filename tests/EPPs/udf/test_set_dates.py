from genologics.entities import Sample

from cg_lims.EPPs.udf.set.set_sample_date import set_received
from datetime import datetime as dt
from tests.conftest import (
    server,
)


def test_set_received(lims):
    # GIVEN: A lims with a sample: "ACC8454A1" with a recieved date

    server("wgs_prep")
    sample = Sample(lims=lims, id="ACC8454A1")
    received_date = sample.udf.get("Received at")

    # WHEN running build_step_documents
    set_received(sample)

    # THEN assert the original date was not changed to todays date
    assert sample.udf.get("Received at") == received_date
    assert sample.udf.get("Received at") != dt.today().date()
