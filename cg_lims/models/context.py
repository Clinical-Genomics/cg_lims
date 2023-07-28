from genologics.lims import Lims
from pydantic.v1 import BaseModel
from cg_lims.status_db_api import StatusDBAPIClient


class EPPContextObject(BaseModel):
    lims: Lims
    status_db: StatusDBAPIClient

    class Config:
        arbitrary_types_allowed = True
