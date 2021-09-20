import logging

from genologics.lims import Lims, Process, Artifact
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.models.database.base_prep import BasePrep

LOG = logging.getLogger(__name__)


class MicrobialLibraryPrepNextera(BasePrep):
    def __init__(self, lims: Lims, sample_id: str):
        super().__init__(lims=lims, sample_id=sample_id)
        self.process_type = "CG002 - Microbial Library Prep (Nextera)"
        self.process_udf_model = MicrobialLibraryPrepNexteraProcessUDFS
        self.artifact = self.set_artifact()


class MicrobialLibraryPrepNexteraProcessUDFS(BaseModel):
    lot_nr_tagmentation_buffer: str = Field(..., alias="Lot nr: Tagmentation buffer (TD-buffer)")
    lot_nr_tagmentation_enzyme: str = Field(..., alias="Lot nr: Tagmentation enzyme (TDE1)")
    lot_nr_index: str = Field(..., alias="Lot nr: Index")
    lot_nr_pcr_mix: str = Field(..., alias="Lot nr: KAPA HiFi HotStart ReadyMix (2X)")
    pcr_instrument_incubation: str = Field(..., alias="PCR instrument incubation")
    pcr_instrument_amplification: str = Field(..., alias="PCR instrument amplification")
    nr_pcr_cycles: int = Field(..., alias="Nr PCR cycles")
