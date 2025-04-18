import datetime as dt
import logging
from typing import List, Optional, Tuple

from genologics.entities import Artifact, Process, Sample
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
    """Parse out the well position from LocationDescriptor"""

    location: Tuple = artifact.location
    return location[1].replace(":", "")


def get_alternative_artifact_well(artifact: Artifact) -> str:
    """Parse out the well position from LocationDescriptor and converts it to the format: A:1 -> A01"""

    col, row = artifact.location[1].split(":")
    if int(row) < 10:
        row = "0" + row
    return col + row


def get_index_well(artifact: Artifact):
    """Parsing out the index well position from the reagent label string which
    typically looks like this: '44_A05 IDT_10nt_446 (AGCGTGACCT-CCATCCGAGT)'
    """

    if artifact.reagent_labels:
        # Assuming one reagent label per artifact (reagent_labels is a list):
        reagent_label: str = artifact.reagent_labels[0]

        # Getting the index well:
        index_well_with_zero_and_us: str = reagent_label.split(" ")[0]
        index_well_with_zero: str = index_well_with_zero_and_us.split("_")[1]

        # Picking out column and removing zeros by int():
        index_well_col: int = int(index_well_with_zero[1:])
        index_well_row: str = index_well_with_zero[0]
        return f"{index_well_row}{index_well_col}"
    else:
        return "-"


def get_smrtbell_adapter_name(artifact: Artifact) -> str:
    """
    Parse out the SMRTbell adapter name from a reagent label string which typically looks like this:
    48_H06 bc2048 (TGATGCTAGTGAGTAT)
    """
    if artifact.reagent_labels:
        reagent_label: str = artifact.reagent_labels[0]
        return reagent_label.split(" ")[1]
    else:
        return "-"


def get_barcode(artifact: Artifact):
    """Central script for generation of barcode. Looks at container type and
    assign barcode according to Atlas document 'Barcodes at Clinical Genomics'"""

    artifact_container_type = artifact.container.type.name.lower()

    # Barcode for samples on 96 well plate
    if artifact_container_type == "96 well plate":
        return artifact.container.name

    # Barcode for pool placed in tube.
    elif len(artifact.samples) > 1 and artifact_container_type == "tube":
        return artifact.name

    # Barcode for sample in tube.
    elif artifact_container_type == "tube":
        return artifact.samples[0].id[3:]

    else:
        LOG.info(f"Sample {str(artifact.samples[0].id)} could not be assigned a barcode.")
        return None


def get_artifact_sample_id(artifact: Artifact) -> Optional[str]:
    """Return the sample ID belonging to an artifact if it isn't a pool."""
    samples = artifact.samples if artifact else None
    if not (samples and samples[0].id):
        return None
    if len(samples) > 1:
        return None
    return samples[0].id


def get_flow_cell_name(process: Process) -> Optional[str]:
    artifacts: Optional[List[Artifact]] = process.all_inputs()
    if not artifacts:
        return None
    artifact: Artifact = artifacts[0]
    if not artifact.container:
        return None
    if not artifact.container.name:
        return None
    return artifact.container.name
