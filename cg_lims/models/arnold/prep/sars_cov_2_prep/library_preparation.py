from typing import Optional

from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.objects import BaseAnalyte
from cg_lims.models.arnold.prep.base_step import BaseStep


class LibraryPreparationCovProcessUDFS(BaseModel):
    """Library Preparation (Cov) v1"""

    lot_nr_tagmentation_beads: str = Field(..., alias="Tagmentation beads")
    lot_nr__stop_tagment_buffer: str = Field(..., alias="Stop Tagment Buffer")
    lot_nr_index: str = Field(..., alias="Index")
    lot_nr_pcr_mix: str = Field(..., alias="PCR-mix")
    lot_nr_tagmentation_wash_buffer: str = Field(..., alias="Tagmentation Wash Buffer")
    lot_nr_h2o_library_preparation: str = Field(..., alias="Nuclease-free water")
    lot_nr_TB1: str = Field(..., alias="TB1 HT")
    pcr_instrument_tagmentation: str = Field(..., alias="PCR machine: Tagmentation")
    pcr_instrument_amplification: str = Field(..., alias="PCR machine: Amplification")
    library_preparation_method: str = Field(..., alias="Method document")
    liquid_handling_system: str = Field(..., alias="Instrument")


class LibraryPreparationCovFields(
    BaseStep,
):
    process_udfs: LibraryPreparationCovProcessUDFS

    class Config:
        allow_population_by_field_name = True


def get_library_prep_cov(lims: Lims, sample_id: str, prep_id: str) -> LibraryPreparationCovFields:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_type="Library Preparation (Cov) v1",
    )

    return LibraryPreparationCovFields(
        **analyte.base_fields(),
        process_udfs=LibraryPreparationCovProcessUDFS(**analyte.process_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="library_prep",
        workflow="sars_cov_2"
    )
