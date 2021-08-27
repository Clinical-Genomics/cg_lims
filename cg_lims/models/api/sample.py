from pydantic import BaseModel, Field, validator
import datetime as dt
from typing import Optional
import logging

LOG = logging.getLogger(__name__)


def get_number_of_days(first_date: dt, second_date: dt) -> Optional[int]:
    """Get number of days between different time stamps."""

    days = None
    if first_date and second_date:
        time_span = second_date - first_date
        days = time_span.days

    return days


class Sample(BaseModel):
    id: str
    name: str
    project: str
    received_date: Optional[dt.date] = Field(None, alias="Received at")
    prepared_date: Optional[dt.date] = Field(None, alias="Library Prep Finished")
    sequenced_date: Optional[dt.date] = Field(None, alias="Sequencing Finished")
    delivery_date: Optional[dt.date] = Field(None, alias="Delivered at")
    application: Optional[str] = Field(None, alias="Sequencing Analysis")
    bait_set: Optional[str] = Field(None, alias="Bait Set")
    capture_kit: Optional[str] = Field(None, alias="Capture Library version")
    collection_date: Optional[dt.date] = Field(None, alias="Collection Date")
    comment: Optional[str] = Field(None, alias="Comment")
    concentration: Optional[float] = Field(None, alias="Concentration (nM)")
    concentration_sample: Optional[float] = Field(None, alias="Sample Conc.")
    customer: Optional[str] = Field(None, alias="customer")
    data_analysis: Optional[str] = Field(None, alias="Data Analysis")
    data_delivery: Optional[str] = Field(None, alias="Data Delivery")
    elution_buffer: Optional[str] = Field(None, alias="Sample Buffer")
    extraction_method: Optional[str] = Field(None, alias="Extraction method")
    family_name: Optional[str] = Field(None, alias="familyID")
    formalin_fixation_time: Optional[str] = Field(None, alias="Formalin Fixation Time")
    index: Optional[str] = Field(None, alias="Index type")
    index_number: Optional[str] = Field(None, alias="Index number")
    lab_code: Optional[str] = Field(None, alias="Lab Code")
    organism: Optional[str] = Field(None, alias="Strain")
    organism_other: Optional[str] = Field(None, alias="Other species")
    original_lab: Optional[str] = Field(None, alias="Original Lab")
    original_lab_address: Optional[str] = Field(None, alias="Original Lab Address")
    pool: Optional[str] = Field(None, alias="pool name")
    post_formalin_fixation_time: Optional[str] = Field(None, alias="Post Formalin Fixation Time")
    pre_processing_method: Optional[str] = Field(None, alias="Pre Processing Method")
    priority: Optional[str] = Field(None, alias="priority")
    quantity: Optional[str] = Field(None, alias="Quantity")
    reference_genome: Optional[str] = Field(None, alias="Reference Genome Microbial")
    region: Optional[str] = Field(None, alias="Region")
    region_code: Optional[str] = Field(None, alias="Region Code")
    require_qcok: Optional[str] = Field(None, alias="Process only if QC OK")
    rml_plate_name: Optional[str] = Field(None, alias="RML plate name")
    selection_criteria: Optional[str] = Field(None, alias="Selection Criteria")
    sequencing_qc_pass: Optional[str] = Field(None, alias="Passed Sequencing QC")
    sex: Optional[str] = Field(None, alias="Gender")
    source: Optional[str] = Field(None, alias="Source")
    target_reads: Optional[str] = Field(None, alias="Reads missing (M)")
    tissue_block_size: Optional[str] = Field(None, alias="Tissue Block Size")
    tumour: Optional[str] = Field(None, alias="tumor")
    tumour_purity: Optional[str] = Field(None, alias="tumour purity")
    verified_organism: Optional[str] = Field(None, alias="Verified organism")
    volume: Optional[float] = Field(None, alias="Volume (uL)")
    well_position_rml: Optional[str] = Field(None, alias="RML well position")
    processing_time: Optional[int]
    sequenced_to_delivered: Optional[int]
    prepped_to_sequenced: Optional[int]
    received_to_prepped: Optional[int]

    @validator("processing_time", always=True)
    def set_processing_time(cls, v, values: dict) -> Optional[int]:
        """Calculating sample processing time."""
        received_date: Optional[dt.date] = values.get("received_date")
        delivery_date: Optional[dt.date] = values.get("delivery_date")
        return get_number_of_days(first_date=received_date, second_date=delivery_date)

    @validator("sequenced_to_delivered", always=True)
    def set_sequenced_to_delivered(cls, v, values: dict) -> Optional[int]:
        """Calculating sample processing time."""
        received_date: Optional[dt.date] = values.get("sequenced_date")
        delivery_date: Optional[dt.date] = values.get("delivered_date")
        return get_number_of_days(first_date=received_date, second_date=delivery_date)

    @validator("prepped_to_sequenced", always=True)
    def set_prepped_to_sequenced(cls, v, values: dict) -> Optional[int]:
        """Calculating sample processing time."""
        received_date: Optional[dt.date] = values.get("prepared_date")
        delivery_date: Optional[dt.date] = values.get("sequenced_date")
        return get_number_of_days(first_date=received_date, second_date=delivery_date)

    @validator("received_to_prepped", always=True)
    def set_received_to_prepped(cls, v, values: dict) -> Optional[int]:
        """Calculating sample processing time."""
        received_date: Optional[dt.date] = values.get("received_date")
        delivery_date: Optional[dt.date] = values.get("prepared_date")
        return get_number_of_days(first_date=received_date, second_date=delivery_date)

    class Config:
        allow_population_by_field_name = True
