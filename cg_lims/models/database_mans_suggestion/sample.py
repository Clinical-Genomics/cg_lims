from typing import Optional
from pydantic import Field
from pydantic.main import BaseModel
from datetime import date


class Sample(BaseModel):
    sample_id: str
    application_tag: Optional[str] = Field(..., alias="Sequencing Analysis")
    category: Optional[str]
    received_date: Optional[date] = Field(..., alias="Received at")
    delivery_date: Optional[date] = Field(..., alias="Delivered at")
    sequenced_date: Optional[date] = Field(..., alias="Sequencing Finished")
    prepared_date: Optional[date] = Field(..., alias="Library Prep Finished")
    sequenced_to_delivered: Optional[int]
    prepped_to_sequenced: Optional[int]
    received_to_prepped: Optional[int]
    received_to_delivered: Optional[int]
    family: Optional[str] = Field(..., alias="Family")
    strain: Optional[str] = Field(..., alias="Strain")
    source: Optional[str] = Field(..., alias="Source")
    customer: Optional[str] = Field(..., alias="customer")
    priority: Optional[str] = Field(..., alias="priority")  # exist?
    initial_qc: Optional[str] = Field(..., alias="Passed Initial QC")
    library_qc: Optional[str] = Field(..., alias="Passed Library QC")
    prep_method: Optional[str] = Field(..., alias="Prep Method")
    sequencing_qc: Optional[str] = Field(..., alias="Passed Sequencing QC")
