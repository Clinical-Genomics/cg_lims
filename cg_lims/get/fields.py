import datetime as dt
from requests.exceptions import HTTPError
from genologics.entities import Sample
from typing import Optional


def get_received_date(sample: Sample) -> Optional[dt.date]:
    """Get the date when a sample was received."""

    try:
        date = sample.udf.get("Received at")
    except HTTPError:
        date = None
    return date


def get_prepared_date(sample: Sample) -> Optional[dt.date]:
    """Get the date when a sample was prepared in the lab."""

    try:
        date = sample.udf.get("Library Prep Finished")
    except HTTPError:
        date = None
    return date


def get_delivery_date(sample: Sample) -> Optional[dt.date]:
    """Get delivery date for a sample."""

    try:
        date = sample.udf.get("Delivered at")
    except HTTPError:
        date = None
    return date


def get_sequenced_date(sample: Sample) -> Optional[dt.date]:
    """Get the date when a sample was sequenced."""

    try:
        date = sample.udf.get("Sequencing Finished")
    except HTTPError:
        date = None
    return date


def get_sample_comment(sample: Sample) -> Optional[str]:
    """Get sample comment udf"""

    try:
        date = sample.udf.get("comment")
    except HTTPError:
        date = None
    return date


def get_processing_time(sample: Sample) -> Optional[dt.datetime]:
    """Get the time it takes to process a sample"""

    received_at = get_received_date(sample)
    delivery_date = get_delivery_date(sample)
    if received_at and delivery_date:
        return delivery_date - received_at
    return None
