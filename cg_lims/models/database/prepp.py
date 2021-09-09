from typing import List, Literal, Optional
from pydantic.main import BaseModel

from cg_lims.models.database import SampleCollection


class PrepCollection(BaseModel):
    prep_id: int
    workflow: str = Literal["RNA", "TWIST", "COV", "WGS-PCR-free", "Microbial-WGS"]  # ??
    # prep_type: str = Literal['SureSelect', 'exo']  # ??
    sample_ids: List[str]


class PrepCollectionWGSPCRFree(PrepCollection):
    test_field: str


#    lot_number: int
#    nr_defrosts: int
#    concentration: float


class PrepCollectionTWIST(PrepCollection):
    test_field: str


#    concentration_pre_hyb: float
#    concentration_post_hyb: float
#    library_size_pre_hyb: int
#    library_size_post_hyb: int
#    amount: int
#    volume: float
#    lot_number: int
