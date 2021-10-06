from typing import Optional

from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.objects import BaseAnalyte


class LibraryPrepNexteraProcessUDFS(BaseModel):
    lot_nr_tagmentation_buffer: str = Field(..., alias="Lot nr: Tagmentation buffer (TD-buffer)")
    lot_nr_tagmentation_enzyme: str = Field(..., alias="Lot nr: Tagmentation enzyme (TDE1)")
    lot_nr_index: str = Field(..., alias="Lot nr: Index")
    lot_nr_pcr_mix: str = Field(..., alias="Lot nr: KAPA HiFi HotStart ReadyMix (2X)")
    pcr_instrument_incubation: str = Field(..., alias="PCR instrument incubation")
    pcr_instrument_amplification: str = Field(..., alias="PCR instrument amplification")
    nr_pcr_cycles: int = Field(..., alias="Nr PCR cycles")


class LibraryPrepUDFS(LibraryPrepNexteraProcessUDFS):
    b_well_position: Optional[str] = Field(None, alias="well_position")
    b_container_name: Optional[str] = Field(None, alias="container_name")
    b_index_name: Optional[str] = Field(None, alias="index_name")

    class Config:
        allow_population_by_field_name = True


def get_library_prep_nextera_udfs(lims: Lims, sample_id: str) -> LibraryPrepUDFS:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_udf_model=LibraryPrepNexteraProcessUDFS,
        process_type="CG002 - Microbial Library Prep (Nextera)",
    )
    return LibraryPrepUDFS(
        **analyte.merge_analyte_fields(),
    )
