from genologics.entities import Sample, Process

from cg_lims.EPPs.udf.set.set_sample_date import (
    set_prepared,
    set_sequenced,
    set_delivered,
)
from datetime import datetime as dt
from tests.conftest import (
    server,
)


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


def test_set_sequenced_date_was_set(lims):
    # GIVEN: A lims with a sample: "ACC8454A1" with a delivery date.

    server("wgs_prep")
    old_date = dt(2020, 6, 17).date()
    sample = Sample(lims=lims, id="ACC8454A1")
    sample.udf["Sequencing Finished"] = old_date
    sample.put()

    # WHEN running set_sequenced
    set_sequenced(sample)

    # THEN assert the sequencing date was not updated!
    assert sample.udf.get("Sequencing Finished") != dt.today().date()
    assert sample.udf.get("Sequencing Finished") == old_date


def test_set_delivered(lims):
    # GIVEN: A lims with a sample: "ACC8454A1" and a process with a Date delivered udf set.

    server("wgs_prep")
    sample = Sample(lims=lims, id="ACC8454A1")
    process = Process(lims=lims, id="24-240272")
    process.udf["Date delivered"] = dt.today().date()
    process.put()

    # WHEN running set_delivered
    set_delivered(sample=sample, process=process)

    # THEN assert the delivery date was set on the sample
    assert sample.udf.get("Delivered at") == process.udf["Date delivered"]
