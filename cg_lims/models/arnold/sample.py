import datetime
from typing import Optional
from pydantic import Field, validator
from pydantic.main import BaseModel
from datetime import date


class ArnoldSample(BaseModel):
    id: Optional[str] = Field(alias="_id")
    sample_id: str
    application_tag: Optional[str] = Field(alias="Sequencing Analysis")
    category: Optional[str]
    received_date: Optional[date] = Field(alias="Received at")
    delivery_date: Optional[date] = Field(alias="Delivered at")
    sequenced_date: Optional[date] = Field(alias="Sequencing Finished")
    prepared_date: Optional[date] = Field(alias="Library Prep Finished")
    sequenced_to_delivered: Optional[int]
    prepped_to_sequenced: Optional[int]
    received_to_prepped: Optional[int]
    received_to_delivered: Optional[int]
    family: Optional[str] = Field(alias="Family")
    strain: Optional[str] = Field(alias="Strain")
    source: Optional[str] = Field(alias="Source")
    customer: Optional[str] = Field(alias="customer")
    priority: Optional[str] = Field(alias="priority")  # exist?
    initial_qc: Optional[str] = Field(alias="Passed Initial QC")
    library_qc: Optional[str] = Field(alias="Passed Library QC")
    prep_method: Optional[str] = Field(alias="Prep Method")
    sequencing_qc: Optional[str] = Field(alias="Passed Sequencing QC")

    @validator("received_date", always=True)
    def get_received_date(cls, v, values) -> Optional[str]:
        if isinstance(v, datetime.datetime):
            return v.__str__()
        return None

    @validator("delivery_date", always=True)
    def get_delivery_date(cls, v, values) -> Optional[str]:
        if isinstance(v, datetime.datetime):
            return v.__str__()
        return None

    @validator("sequenced_date", always=True)
    def get_sequenced_date(cls, v, values) -> Optional[str]:
        if isinstance(v, datetime.datetime):
            return v.__str__()
        return None

    @validator("prepared_date", always=True)
    def get_prepared_date(cls, v, values) -> Optional[str]:
        if isinstance(v, datetime.datetime):
            return v.__str__()
        return None

    @validator("sequenced_to_delivered", always=True)
    def get_sequenced_to_delivered(cls, v, values) -> Optional[int]:
        if values.get("sequenced_date") and values.get("delivered_date"):
            time_span = values["sequenced_date"] - values["delivered_date"]
            return time_span.days
        return None

    @validator("prepped_to_sequenced", always=True)
    def get_prepped_to_sequenced(cls, v, values) -> Optional[int]:
        if values.get("prepared_date") and values.get("sequenced_date"):
            time_span = values["prepared_date"] - values["sequenced_date"]
            return time_span.days
        return None

    @validator("received_to_prepped", always=True)
    def get_received_to_prepped(cls, v, values) -> Optional[int]:
        if values.get("received_date") and values.get("prepared_date"):
            time_span = values["received_date"] - values["prepared_date"]
            return time_span.days
        return None

    @validator("received_to_delivered", always=True)
    def get_received_to_delivered(cls, v, values) -> Optional[int]:
        if values.get("received_date") and values.get("delivered_date"):
            time_span = values["received_date"] - values["delivered_date"]
            return time_span.days
        return None

    class Config:
        allow_population_by_field_name = True
