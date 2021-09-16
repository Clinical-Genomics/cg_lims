

from typing import Optional
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.models.database.prep import PrepCollection




""Vet ej vilket steg jag ska skriva""
class AggregateQCDNACovv1ArtifactUDF(BaseModel):
    sample_concentration: Optional[float] = Field(None, alias="Concentration")
    sample_size: Optional[float] = Field(None, alias="Peak Size")

        

class LibraryPreparationCovv1ProcessUDFS(BaseModel):
    lot_nr_tagmentation_beads: str = Field(..., alias="Tagmentation beads")
    lot_nr__stop_tagment_buffer: str = Field(..., alias="Stop Tagment Buffer")
    lot_nr_index: str = Field(..., alias="Index")
    lot_nr_pcr_mix: str = Field(..., alias="PCR-mix")
    lot_nr_tagmentation_wash_buffer: str = Field(..., alias="Tagmentation Wash Buffer")
    lot_nr_nuclease_free_water: str = Field(..., alias="Nuclease-free water")
    lot_nr_TB1: str = Field(..., alias="TB1 HT")
    pcr_instrument_tagmentation: str = Field(..., alias="PCR machine: Tagmentation")
    pcr_instrument_amplification: str = Field(..., alias="PCR machine: Amplification")    
    library_preparation_method: str = Field(..., alias="Method document")
    liquid_handling_system: str = Field(..., alias="Instrument")
        ""Går det att få fram antal prover/pool?""


        ""Obs pool från och med här""
class PoolingAndCleanUpCovv1ProcessUDFS(BaseModel):
    pooling_method: str = Field(..., alias="Method document (pooling)")
    clean-up_method: str = Field(..., alias="Method document (Clean-up)")
    lot_nr_beads_clean_up: str = Field(..., alias="Purification beads")
    lot_nr_etoh_clean_up: str = Field(..., alias="Ethanol")
    lot_nr_h2o_clean_up: str = Field(..., alias="Nuclease-free water")
    lot_nr_resuspension_buffer_clean_up: str = Field(..., alias="Resuspension buffer")


class PoolingAndCleanUpCovv1ArtifactUDF(BaseModel):
    finished_library_concentration: float = Field(..., alias="Concentration")
    finished_library_concentration_nm: float = Field(..., alias="Concentration (nM)")
    finished_library_size: Optional[float] = Field(None, alias="Size (bp)")

