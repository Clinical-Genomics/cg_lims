import datetime as dt
from requests.exceptions import HTTPError
from genologics.entities import Sample
from typing import Optional
import logging

LOG = logging.getLogger(__name__)


def get_udf_value(sample: Sample, get_string: str):
    """Get sample udf based on udf name"""
    try:
        return sample.udf.get(get_string)
    except HTTPError:
        LOG.info("Sample %s doesn't have the udf %s" % (sample.id, get_string))
        return None


def get_prepared_date(sample: Sample) -> Optional[dt.date]:
    """Get the date when a sample was prepared in the lab."""

    return get_udf_value(sample, "Library Prep Finished")


def get_received_date(sample: Sample) -> Optional[dt.date]:
    """Get the date when a sample was received."""

    return get_udf_value(sample, "Received at")


def get_delivery_date(sample: Sample) -> Optional[dt.date]:
    """Get delivery date for a sample."""
    return get_udf_value(sample, "Delivered at")


def get_sequenced_date(sample: Sample) -> Optional[dt.date]:
    """Get the date when a sample was sequenced."""
    return get_udf_value(sample, "Sequencing Finished")


def get_sample_comment(sample: Sample) -> Optional[str]:
    """Get sample comment udf"""
    return get_udf_value(sample, "comment")


def get_processing_time(sample: Sample) -> Optional[dt.datetime]:
    """Get the time it takes to process a sample"""

    received_at = get_received_date(sample)
    delivery_date = get_delivery_date(sample)
    if received_at and delivery_date:
        return delivery_date - received_at
    LOG.info(
        "Could not get recieved date or delivery date to generate the processing time for sample %s."
        % sample.id
    )
    return None
