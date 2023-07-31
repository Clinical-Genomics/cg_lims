from genologics.lims import Lims
from pydantic.v1 import BaseModel
from cg_lims.status_db_api import CgClient


class EPPContextObject(BaseModel):
    lims: Lims
    status_db: CgClient

    class Config:
        arbitrary_types_allowed = True
