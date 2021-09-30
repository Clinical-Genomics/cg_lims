import logging

from typing import Optional

from pydantic import Field, BaseModel, validator

LOG = logging.getLogger(__name__)


class Prep(BaseModel):
    """Prep Collection"""

    prep_id: str
    sample_id: str
    workflow: str
    id: Optional[str] = Field(alias="_id")

    @validator("id", always=True)
    def get_process(cls, v, values):
        return values["prep_id"]
