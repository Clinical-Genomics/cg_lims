import datetime
from typing import Optional
from pydantic import Field, validator
from pydantic.main import BaseModel
from datetime import date, datetime


def get_number_of_days(first_date: str, second_date: str) -> Optional[int]:
    """Get number of days between different iso formatted time stamps."""
    if first_date and second_date:
        first_datetime = datetime.strptime(first_date, "%Y-%m-%d %H:%M:%S")
        second_datetime = datetime.strptime(second_date, "%Y-%m-%d %H:%M:%S")
        time_span = second_datetime - first_datetime
        return time_span.days


class ArnoldSample(BaseModel):
    id: Optional[str] = Field(alias="_id")
    sample_id: str
    category: Optional[str]
    received_date: Optional[date] = Field(alias="Received at")
    delivery_date: Optional[date] = Field(alias="Delivered at")
    sequenced_date: Optional[date] = Field(alias="Sequencing Finished")
    prepared_date: Optional[date] = Field(alias="Library Prep Finished")
    collection_date: Optional[date] = Field(alias="Collection Date")
    sequenced_to_delivered: Optional[int]
    prepped_to_sequenced: Optional[int]
    received_to_prepped: Optional[int]
    received_to_delivered: Optional[int]
    initial_qc: Optional[str] = Field(alias="Passed Initial QC")
    library_qc: Optional[str] = Field(alias="Passed Library QC")
    prep_method: Optional[str] = Field(alias="Prep Method")
    application: Optional[str] = Field(alias="Sequencing Analysis")  # application_tag in vogue
    bait_set: Optional[str] = Field(alias="Bait Set")
    capture_kit: Optional[str] = Field(alias="Capture Library version")
    comment: Optional[str] = Field(alias="Comment")
    concentration: Optional[float] = Field(alias="Concentration (nM)")
    concentration_sample: Optional[float] = Field(alias="Sample Conc.")
    customer: Optional[str] = Field(alias="customer")
    data_analysis: Optional[str] = Field(alias="Data Analysis")
    data_delivery: Optional[str] = Field(alias="Data Delivery")
    elution_buffer: Optional[str] = Field(alias="Sample Buffer")
    extraction_method: Optional[str] = Field(alias="Extraction method")
    family_name: Optional[str] = Field(alias="familyID")
    formalin_fixation_time: Optional[float] = Field(alias="Formalin Fixation Time")
    index: Optional[str] = Field(alias="Index type")
    index_number: Optional[str] = Field(alias="Index number")
    lab_code: Optional[str] = Field(alias="Lab Code")
    organism: Optional[str] = Field(alias="Strain")  # strain in vogue
    organism_other: Optional[str] = Field(alias="Other species")
    original_lab: Optional[str] = Field(alias="Original Lab")
    original_lab_address: Optional[str] = Field(alias="Original Lab Address")
    pool: Optional[str] = Field(alias="pool name")
    post_formalin_fixation_time: Optional[float] = Field(alias="Post Formalin Fixation Time")
    pre_processing_method: Optional[str] = Field(alias="Pre Processing Method")
    priority: Optional[str] = Field(alias="priority")
    quantity: Optional[str] = Field(alias="Quantity")
    reference_genome: Optional[str] = Field(alias="Reference Genome Microbial")
    region: Optional[str] = Field(alias="Region")
    region_code: Optional[str] = Field(alias="Region Code")
    require_qcok: Optional[str] = Field(alias="Process only if QC OK")
    rml_plate_name: Optional[str] = Field(alias="RML plate name")
    selection_criteria: Optional[str] = Field(alias="Selection Criteria")
    sequencing_qc_pass: Optional[str] = Field(
        alias="Passed Sequencing QC"
    )  # sequencing_qc in vogue
    sex: Optional[str] = Field(alias="Gender")
    source: Optional[str] = Field(alias="Source")
    target_reads: Optional[float] = Field(alias="Reads missing (M)")
    tissue_block_size: Optional[str] = Field(alias="Tissue Block Size")
    tumour: Optional[str] = Field(alias="tumor")
    tumour_purity: Optional[int] = Field(alias="tumour purity")
    verified_organism: Optional[str] = Field(alias="Verified organism")
    volume: Optional[float] = Field(alias="Volume (uL)")
    well_position_rml: Optional[str] = Field(alias="RML well position")

    @validator("received_date", always=True)
    def get_received_date(cls, v, values) -> Optional[str]:
        if isinstance(v, date):
            return datetime(v.year, v.month, v.day).__str__()
        return None

    @validator("delivery_date", always=True)
    def get_delivery_date(cls, v, values) -> Optional[str]:
        if isinstance(v, date):
            return datetime(v.year, v.month, v.day).__str__()
        return None

    @validator("sequenced_date", always=True)
    def get_sequenced_date(cls, v, values) -> Optional[str]:
        if isinstance(v, date):
            return datetime(v.year, v.month, v.day).__str__()
        return None

    @validator("collection_date", always=True)
    def get_collection_date(cls, v, values) -> Optional[str]:
        if isinstance(v, date):
            return datetime(v.year, v.month, v.day).__str__()
        return None

    @validator("prepared_date", always=True)
    def get_prepared_date(cls, v, values) -> Optional[str]:
        if isinstance(v, date):
            return datetime(v.year, v.month, v.day).__str__()
        return None

    @validator("sequenced_to_delivered", always=True)
    def get_sequenced_to_delivered(cls, v, values) -> Optional[int]:
        return get_number_of_days(values.get("sequenced_date"), values.get("delivered_date"))

    @validator("prepped_to_sequenced", always=True)
    def get_prepped_to_sequenced(cls, v, values) -> Optional[int]:
        return get_number_of_days(values.get("prepared_date"), values.get("sequenced_date"))

    @validator("received_to_prepped", always=True)
    def get_received_to_prepped(cls, v, values) -> Optional[int]:
        return get_number_of_days(values.get("received_date"), values.get("prepared_date"))

    @validator("received_to_delivered", always=True)
    def get_received_to_delivered(cls, v, values) -> Optional[int]:
        return get_number_of_days(values.get("received_date"), values.get("delivered_date"))

    class Config:
        allow_population_by_field_name = True
