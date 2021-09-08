from typing import List, Literal, Optional
from pydantic.main import BaseModel

from cg_lims.models.database import SampleCollection


class PrepCollection(BaseModel):
    prepp_id: int
    prep_type: Literal['mic', 'SureSelect', 'exo']
    hyb: Optional[Literal['post', 'pre']]
    sample_ids: List[SampleCollection]
    concentration_pre_hyb: float
    concentration_post_hyb: float
    library_size_pre_hyb: int
    library_size_post_hyb: int
    amount: int
    volume: float
    lot_number: int
    nr_defrosts: int
