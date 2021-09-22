from typing import Optional

from pydantic import BaseModel, Field


class Prep(BaseModel):
    """LIMS Prep Collection"""

    id: Optional[str] = Field(..., alias="_id")
    prep_id: str
    sample_id: str
    workflow: str
