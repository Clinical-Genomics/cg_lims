from genologics.lims import Lims
from pydantic import BaseModel
from cg_lims.cgface_api import CgFace


class EPPContextObject(BaseModel):
    lims: Lims
    cgface: CgFace

    class Config:
        arbitrary_types_allowed = True


class APIContextObject(EPPContextObject):
    host: str
    port: int
