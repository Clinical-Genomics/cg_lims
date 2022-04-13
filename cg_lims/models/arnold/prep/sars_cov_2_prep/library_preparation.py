from typing import Optional

from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.objects import BaseAnalyte
from cg_lims.models.arnold.base_step import BaseStep


class ProcessUDFs(BaseModel):
    """Library Preparation (Cov) v1"""

    lot_nr_tagmentation_beads: Optional[str] = Field(None, alias="Tagmentation beads")
    lot_nr__stop_tagment_buffer: Optional[str] = Field(None, alias="Stop Tagment Buffer")
    lot_nr_index: Optional[str] = Field(None, alias="Index")
    lot_nr_pcr_mix: Optional[str] = Field(None, alias="PCR-mix")
    lot_nr_tagmentation_wash_buffer: Optional[str] = Field(None, alias="Tagmentation Wash Buffer")
    lot_nr_h2o_library_preparation: Optional[str] = Field(None, alias="Nuclease-free water")
    lot_nr_TB1: Optional[str] = Field(None, alias="TB1 HT")
    pcr_instrument_tagmentation: Optional[str] = Field(None, alias="PCR machine: Tagmentation")
    pcr_instrument_amplification: Optional[str] = Field(None, alias="PCR machine: Amplification")
    library_preparation_method: Optional[str] = Field(None, alias="Method document")
    liquid_handling_system: Optional[str] = Field(None, alias="Instrument")


class ArnoldStep(
    BaseStep,
):
    process_udfs: ProcessUDFs

    class Config:
        allow_population_by_field_name = True


def get_library_prep_cov(lims: Lims, sample_id: str, prep_id: str) -> ArnoldStep:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_type="Library Preparation (Cov) v1",
    )

    return ArnoldStep(
        **analyte.base_fields(),
        process_udfs=ProcessUDFs(**analyte.process_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="library_prep",
        workflow="sars_cov_2"
    )
