from typing import Optional, Literal

from pydantic import BaseModel, Field


class PrepCollection(BaseModel):
    id: Optional[str] = Field(..., alias="_id")
    prep_id: str
    sample_id: str
    workflow: str = Literal["RNA", "TWIST", "COV", "WGS-PCR-free", "Microbial-WGS"]
