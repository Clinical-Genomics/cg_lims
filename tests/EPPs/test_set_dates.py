from genologics.entities import Sample

from cg_lims.EPPs.udf.set.set_sample_date import (
    set_received,
    set_prepared,
    set_sequenced,
    set_delivered,
)
from datetime import datetime as dt
from tests.conftest import (
    server,
)


def test_set_received(lims):
    # GIVEN: A lims with a sample: "ACC8454A1" with a no recieved date

    server("wgs_prep")
    sample = Sample(lims=lims, id="ACC8454A1")
    sample.udf["Received at"] = None
    sample.put()

    # WHEN running set_received
    set_received(sample)

    # THEN assert the recieved date was set to todays date
    assert sample.udf.get("Received at") == dt.today().date()


def test_set_received_date_already_set(lims):
    # GIVEN: A lims with a sample: "ACC8454A1" with a recieved date

    server("wgs_prep")
    sample = Sample(lims=lims, id="ACC8454A1")
    received_date = sample.udf.get("Received at")

    # WHEN running set_received
    set_received(sample)

    # THEN assert the original date was not changed to todays date
    assert sample.udf.get("Received at") == received_date
    assert sample.udf.get("Received at") != dt.today().date()


def test_set_prepared(lims):
    # GIVEN: A lims with a sample: "ACC8454A1" with a no sequencing date and no delivery date.

    server("wgs_prep")
    sample = Sample(lims=lims, id="ACC8454A1")

    # WHEN running set_prepared
    set_prepared(sample)

    # THEN assert the prepared date was set to todays date
    assert sample.udf.get("Library Prep Finished") == dt.today().date()


def test_set_prepared_delivered_and_sequenced_were_set(lims):
    # GIVEN: A lims with a sample: "ACC8454A1" with a sequencing date and a delivery date.

    server("wgs_prep")
    sample = Sample(lims=lims, id="ACC8454A1")
    sample.udf["Delivered at"] = dt(2020, 6, 17).date()
    sample.udf["Sequencing Finished"] = dt(2020, 5, 17).date()
    sample.put()

    # WHEN running set_prepared
    set_prepared(sample)

    # THEN assert the prepared date was set to todays date but the other two dates were set to None!
    assert sample.udf.get("Library Prep Finished") == dt.today().date()
    assert sample.udf.get("Delivered at") is None
    assert sample.udf.get("Sequencing Finished") is None


def test_set_sequenced(lims):
    # GIVEN: A lims with a sample: "ACC8454A1" with a no sequencing date and no delivery date.

    server("wgs_prep")
    sample = Sample(lims=lims, id="ACC8454A1")

    # WHEN running set_sequenced
    set_sequenced(sample)

    # THEN assert the sequrncing date was set to todays date
    assert sample.udf.get("Sequencing Finished") == dt.today().date()


def test_set_sequenced_delivered_was_set(lims):
    # GIVEN: A lims with a sample: "ACC8454A1" with a delivery date.

    server("wgs_prep")
    sample = Sample(lims=lims, id="ACC8454A1")
    sample.udf["Delivered at"] = dt(2020, 6, 17).date()
    sample.put()

    # WHEN running set_sequenced
    set_sequenced(sample)

    # THEN assert the sequencing date was set to todays date but the sequencingdate was set to None!
    assert sample.udf.get("Sequencing Finished") == dt.today().date()
    assert sample.udf.get("Delivered at") is None


def test_set_delivered(lims):
    # GIVEN: A lims with a sample: "ACC8454A1".

    server("wgs_prep")
    sample = Sample(lims=lims, id="ACC8454A1")

    # WHEN running set_delivered
    set_delivered(sample)

    # THEN assert the delivery date was set to todays date
    assert sample.udf.get("Delivered at") == dt.today().date()
