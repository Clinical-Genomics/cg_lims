from typing import Optional

from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.objects import BaseAnalyte


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


class LibraryPreparationCovUDFS(LibraryPreparationCovProcessUDFS):
    library_prep_well_position: Optional[str] = Field(None, alias="well_position")
    library_prep_container_name: Optional[str] = Field(None, alias="container_name")
    library_prep_index_name: Optional[str] = Field(None, alias="index_name")

    class Config:
        allow_population_by_field_name = True


def get_library_prep_cov_udfs(lims: Lims, sample_id: str) -> LibraryPreparationCovUDFS:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_udf_model=LibraryPreparationCovProcessUDFS,
        process_type="Library Preparation (Cov) v1",
    )

    return LibraryPreparationCovUDFS(
        **analyte.merge_analyte_fields(),
    )
