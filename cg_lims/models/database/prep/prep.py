from typing import Optional

from pydantic import Field, BaseModel

from cg_lims.models.database.prep.microbial_prep import MicrobialPrep
from cg_lims.models.database.prep.sars_cov_2_prep import SarsCov2Prep


class Prep(BaseModel):
    """LIMS Prep Collection"""

    id: Optional[str] = Field(..., alias="_id")
    prep_id: str
    sample_id: str
    microbial_prep: Optional[MicrobialPrep]
    sars_cov_2_prep: Optional[SarsCov2Prep]
