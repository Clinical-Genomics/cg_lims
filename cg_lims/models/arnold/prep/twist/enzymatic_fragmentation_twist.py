from typing import Optional

from genologics.lims import Lims
from pydantic import Field, BaseModel

from cg_lims.objects import BaseAnalyte

""Obs, hela detta steg är optional""

class enzymaticfragmentationTWISTv2ProcessUdfs(BaseModel):
    enzymatic_fragmentation_method: Optional[str] = Field(None, alias="Method document")
    fragmentation_time: Optional[str] = Field(None, alias="Fragmentation time (min)")
    pcr_instrument_fragmentation: Optional[str] = Field(None, alias="Thermal cycler name")
    library_preparation_kit_fragmentation: Optional[str] = Field(None, alias="KAPA HyperPlus Kit")
        
# well position (optional)
# container name (optional)
