import logging


from pydantic.main import BaseModel
from pydantic import Field
from cg_lims.models.database.prep.base_step import BaseStep


LOG = logging.getLogger(__name__)


class MicrobialLibraryPrepNexteraProcessUDFS(BaseModel):
    lot_nr_tagmentation_buffer: str = Field(..., alias="Lot nr: Tagmentation buffer (TD-buffer)")
    lot_nr_tagmentation_enzyme: str = Field(..., alias="Lot nr: Tagmentation enzyme (TDE1)")
    lot_nr_index: str = Field(..., alias="Lot nr: Index")
    lot_nr_pcr_mix: str = Field(..., alias="Lot nr: KAPA HiFi HotStart ReadyMix (2X)")
    pcr_instrument_incubation: str = Field(..., alias="PCR instrument incubation")
    pcr_instrument_amplification: str = Field(..., alias="PCR instrument amplification")
    nr_pcr_cycles: int = Field(..., alias="Nr PCR cycles")


class MicrobialLibraryPrepNextera(BaseStep):
    process_type: str = "CG002 - Microbial Library Prep (Nextera)"
    process_udf_model = MicrobialLibraryPrepNexteraProcessUDFS
