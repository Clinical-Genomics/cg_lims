import datetime as dt
import logging
from typing import Optional, Tuple

from genologics.entities import Artifact, Sample
from requests.exceptions import HTTPError

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
        "Could not get received date or delivery date to generate the processing time for sample %s."
        % sample.id
    )
    return None


def get_artifact_well(artifact: Artifact) -> str:
    """Parsing out the well position from LocationDescriptor"""

    location: Tuple = artifact.location
    return location[1].replace(":", "")


def get_index_well(artifact: Artifact):
    """Parsing out the index well position from the reagent label string which
    typically looks like this: 'A05 IDT_10nt_446 (AGCGTGACCT-CCATCCGAGT)'
    """

    if artifact.reagent_labels:
        # Assuming one reagent label per artifact (reagent_labels is a list):
        reagent_label = artifact.reagent_labels[0]

        # Getting the index well:
        index_well_with_zero = reagent_label.split(" ")[0]

        # Picking out column and removing zeros by int():
        index_well_col = int(index_well_with_zero[1:])
        index_well_row = index_well_with_zero[0]
        return f"{index_well_row}{index_well_col}"
    else:
        return "-"
