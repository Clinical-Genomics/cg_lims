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
    # ""Går det att få fram antal prover/pool?""

    #   ""Obs pool från och med här""


class LibraryPreparationCovUDFS(LibraryPreparationCovProcessUDFS):
    class Config:
        allow_population_by_field_name = True


def get_library_prep_cov_udfs(lims: Lims, sample_id: str) -> LibraryPreparationCovUDFS:
    library_prep_cov = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_udf_model=LibraryPreparationCovProcessUDFS,
        process_type="Library Preparation (Cov) v1",
    )

    return LibraryPreparationCovUDFS(**library_prep_cov.merge_process_and_artifact_udfs())
