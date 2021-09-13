from typing import List, Literal, Optional
from pydantic.main import BaseModel
from pydantic import Field


class PrepCollection(BaseModel):
    id: Optional[str] = Field(..., alias="_id")
    prep_id: str
    sample_id: str
    workflow: str = Literal["RNA", "TWIST", "COV", "WGS-PCR-free", "Microbial-WGS"]


class BufferExchangeArtifactUDF(BaseModel):
    sample_concentration: float = Field(..., alias="Concentration")  # Buffer Exchange process udf


class BufferExchangeProcessUDFS(BaseModel):
    lot_nr_beads_buffer_exchange: str = Field(..., alias="Lot Nr: Purification Beads")
    lot_nr_etoh_buffer_exchange: str = Field(..., alias="Lot Nr: EtOH")
    lot_nr_h2o_buffer_exchange: str = Field(..., alias="Lot Nr: Nuclease-free water")
    buffer_exchange_method: str = Field(..., alias="Method document")


class NormalizationOfMicrobialSamplesProcessUDFS(BaseModel):
    sample_normalization_method: Optional[str] = Field(..., alias="Method document")
    normalized_sample_concentration: Optional[float] = Field(
        ..., alias="Final Concentration (ng/ul)"
    )
    lot_nr_dilution_buffer_sample_normalization: Optional[float] = Field(
        ..., alias="Dilution buffer lot no"
    )


class MicrobialLibraryPrepNexteraProcessUDFS:
    lot_nr_tagmentation_buffer: str = Field(..., alias="Lot nr: Tagmentation buffer (TD-buffer)")
    lot_nr_tagmentation_enzyme: str = Field(..., alias="Lot nr: Tagmentation enzyme (TDE1)")
    lot_nr_index: str = Field(..., alias="Lot nr: Index")
    lot_nr_pcr_mix: str = Field(..., alias="Lot nr: KAPA HiFi HotStart ReadyMix (2X)")
    pcr_instrument_incubation: str = Field(..., alias="PCR instrument incubation")
    pcr_instrument_amplification: str = Field(..., alias="PCR instrument amplification")
    nr_pcr_cycles: int = Field(..., alias="Nr PCR cycles")


class PostPCRBeadPurificationProcessUDFS(BaseModel):
    lot_nr_beads_library_prep: str = Field(..., alias="Lot nr: Beads")
    lot_nr_etoh_library_prep: str = Field(..., alias="Lot nr: EtOH")
    lot_nr_h2o_library_prep: str = Field(..., alias="Lot nr: H2O")


class PostPCRBeadPurificationArtifactUDF(BaseModel):
    finished_library_concentration: float = Field(..., alias="Concentration")
    finished_library_concentration_nm: float = Field(..., alias="Concentration (nM)")
    finished_library_size: Optional[float] = Field(..., alias="Size (bp)")
    finished_library_average_size: float = Field(..., alias="Average Size (bp)")


class NormalizationOfMicrobialSamplesForSequencingProcessUDFS(BaseModel):
    lot_nr_dilution_buffer_library_normalization: Optional[str] = Field(
        ..., alias="Dilution buffer lot no"
    )
    normalized_library_concentration: Optional[float] = Field(..., alias="Final Concentration (nM)")
    library_normalization_method: Optional[str] = Field(..., alias="Method document")


class PrepCollectionWGSPCRFree(PrepCollection):
    test_field: str


#    lot_number: int
#    nr_defrosts: int
#    concentration: float


class PrepCollectionTWIST(PrepCollection):
    test_field: str


#    concentration_pre_hyb: float
#    concentration_post_hyb: float
#    library_size_pre_hyb: int
#    library_size_post_hyb: int
#    amount: int
#    volume: float
#    lot_number: int
