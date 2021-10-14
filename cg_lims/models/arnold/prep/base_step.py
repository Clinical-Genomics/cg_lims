import logging
from typing import Optional
from pydantic import Field, BaseModel, validator
from datetime import date, datetime

LOG = logging.getLogger(__name__)


class BaseStep(BaseModel):
    """Artifact related fields that are not udfs."""

    prep_id: str
    step_type: str
    sample_id: str
    workflow: str
    lims_step_name: Optional[str]
    id: Optional[str] = Field(alias="_id")
    step_id: Optional[str] = Field(alias="_id")
    well_position: Optional[str]
    artifact_name: Optional[str]
    container_name: Optional[str]
    container_id: Optional[str]
    container_type: Optional[str]
    index_name: Optional[str]
    nr_samples_in_pool: Optional[int]
    date_run: Optional[date]

    @validator("id", always=True)
    def set_id(cls, v, values):
        return f"{values['prep_id']}_{values['step_type']}"

    @validator("step_id", always=True)
    def set_step_id(cls, v, values):
        return f"{values['prep_id']}_{values['step_type']}"

    @validator("date_run", always=True)
    def get_date_run(cls, v, values) -> Optional[str]:
        if isinstance(v, date):
            return datetime(v.year, v.month, v.day).__str__()
        return None
