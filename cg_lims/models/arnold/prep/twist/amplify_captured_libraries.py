from typing import Optional
from genologics.lims import Lims
from pydantic import Field, BaseModel
from cg_lims.objects import BaseAnalyte

      
      
      
class AmplifycapturedlibrariestwistProcessUDFs(BaseModel):
    amplify_captured_library_method: str = Field(..., alias="Method Document") 
    lot_nr_xgen_primer_amplify_captured_library: str = Field(..., alias="xGen Library Amp primer")
    lot_nr_amplification_kit_amplify_captured_library: str = Field(..., alias="Kapa HiFi HotStart ReadyMix")
    nr_pcr_cycles_amplify_captured_library: str = Field(..., alias="Nr of PCR cycles")
   
# well position (optional)
# container name (optional)
