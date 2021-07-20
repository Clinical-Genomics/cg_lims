from genologics.lims import Lims
from pydantic import BaseModel
from cg_lims.status_db_api import StatusDBAPI


class EPPContextObject(BaseModel):
    lims: Lims
    status_db: StatusDBAPI

    class Config:
        arbitrary_types_allowed = True


class APIContextObject(EPPContextObject):
    host: str
    port: int
