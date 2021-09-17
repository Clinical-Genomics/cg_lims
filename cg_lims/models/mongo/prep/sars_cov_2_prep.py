from typing import Optional
from pydantic.main import BaseModel
from pydantic import Field


# ""Vet ej vilket steg jag ska skriva""
from cg_lims.models.mongo.prep import Prep


class AggregateQCDNACovv1ArtifactUDF(BaseModel):
    """Aggregate QC (DNA) (Cov) v1"""

    sample_concentration: Optional[float] = Field(None, alias="Concentration")
    sample_size: Optional[float] = Field(None, alias="Peak Size")


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


class PoolingAndCleanUpCovProcessUDFS(BaseModel):
    """Pooling and Clean-up (Cov) v1"""

    pooling_method: str = Field(..., alias="Method document (pooling)")
    clean_up_method: str = Field(..., alias="Method document (Clean-up)")
    lot_nr_beads_clean_up: str = Field(..., alias="Purification beads")
    lot_nr_etoh_clean_up: str = Field(..., alias="Ethanol")
    lot_nr_h2o_clean_up: str = Field(..., alias="Nuclease-free water")
    lot_nr_resuspension_buffer_clean_up: str = Field(..., alias="Resuspension buffer")


class PoolingAndCleanUpCovArtifactUDF(BaseModel):
    """Pooling and Clean-up (Cov) v1"""

    finished_library_concentration: float = Field(..., alias="Concentration")
    finished_library_concentration_nm: float = Field(..., alias="Concentration (nM)")
    finished_library_size: Optional[float] = Field(None, alias="Size (bp)")


class SarsCov2Prep(
    Prep,
    PoolingAndCleanUpCovArtifactUDF,
    PoolingAndCleanUpCovProcessUDFS,
    LibraryPreparationCovProcessUDFS,
    AggregateQCDNACovv1ArtifactUDF,
):
    class Config:
        allow_population_by_field_name = True
