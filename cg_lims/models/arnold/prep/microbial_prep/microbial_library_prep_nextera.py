from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field
from cg_lims.models.arnold.prep.base_step import BaseStep
from cg_lims.objects import BaseAnalyte


class ProcessUDFS(BaseModel):
    lot_nr_tagmentation_buffer: str = Field(..., alias="Lot nr: Tagmentation buffer (TD-buffer)")
    lot_nr_tagmentation_enzyme: str = Field(..., alias="Lot nr: Tagmentation enzyme (TDE1)")
    lot_nr_index: str = Field(..., alias="Lot nr: Index")
    lot_nr_pcr_mix: str = Field(..., alias="Lot nr: KAPA HiFi HotStart ReadyMix (2X)")
    pcr_instrument_incubation: str = Field(..., alias="PCR instrument incubation")
    pcr_instrument_amplification: str = Field(..., alias="PCR instrument amplification")
    nr_pcr_cycles: int = Field(..., alias="Nr PCR cycles")


class ArnoldStep(BaseStep):
    process_udfs: ProcessUDFS

    class Config:
        allow_population_by_field_name = True


def get_library_prep_nextera(lims: Lims, sample_id: str, prep_id: str) -> ArnoldStep:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_type="CG002 - Microbial Library Prep (Nextera)",
    )

    return ArnoldStep(
        **analyte.base_fields(),
        process_udfs=ProcessUDFS(**analyte.process_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="library_prep",
        workflow="Microbial"
    )
