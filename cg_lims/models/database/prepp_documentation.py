from typing import List, Literal, Optional
from pydantic.main import BaseModel
from pydantic import Field


class PrepCollection(BaseModel):
    id: Optional[str] = Field(..., alias="_id")
    prep_id: str
    sample_id: str
    workflow: str = Literal["RNA", "TWIST", "COV", "WGS-PCR-free", "Microbial-WGS"]


class PrepCollectionMicrobial(PrepCollection):
    sample_concentration: float = Field(
        ..., alias="Concentration"
    )  # CG002 - Aggregate QC (DNA) sample udf
    buffer_exchange_method: Optional[str] = Field(
        ..., alias="Method document"
    )  # Buffer Exchange process udf
    lot_nr_beads_buffer_exchange: Optional[str] = Field(
        ..., alias="Lot Nr: Purification Beads"
    )  # Buffer Exchange process udf
    lot_nr_etoh_buffer_exchange: Optional[str] = Field(
        ..., alias="Lot Nr: EtOH"
    )  # Buffer Exchange process udf
    lot_nr_h2o_buffer_exchange: Optional[str] = Field(
        ..., alias="Lot Nr: Nuclease-free water"
    )  # Buffer Exchange process udf
    sample_normalization_method: Optional[str] = Field(
        ..., alias="Method document"
    )  # CG002 - Normalization of microbial samples process udf
    normalized_sample_concentration: Optional[float] = Field(
        ..., alias="Final Concentration (ng/ul)"
    )  # CG002 - Normalization of microbial samples process udf
    lot_nr_dilution_buffer_sample_normalization: Optional[float] = Field(
        ..., alias="Dilution buffer lot no"
    )  # CG002 - Normalization of microbial samples process udf
    lot_nr_tagmentation_buffer: str = Field(
        ..., alias="Lot nr: Tagmentation buffer (TD-buffer)"
    )  # Microbial Library Prep (Nextera) v2
    lot_nr_tagmentation_enzyme: str = Field(
        ..., alias="Lot nr: Tagmentation enzyme (TDE1)"
    )  # Microbial Library Prep (Nextera) v2
    lot_nr_index: str = Field(..., alias="Lot nr: Index")  # Microbial Library Prep (Nextera) v2
    lot_nr_pcr_mix: str = Field(
        ..., alias="Lot nr: KAPA HiFi HotStart ReadyMix (2X)"
    )  # Microbial Library Prep (Nextera) v2
    pcr_instrument_incubation: str = Field(
        ..., alias="PCR instrument incubation"
    )  # Microbial Library Prep (Nextera) v2
    pcr_instrument_amplification: str = Field(
        ..., alias="PCR instrument amplification"
    )  # Microbial Library Prep (Nextera) v2
    nr_pcr_cycles: int = Field(..., alias="Nr PCR cycles")  # Microbial Library Prep (Nextera) v2
    lot_nr_beads_library_prep: str = Field(
        ..., alias="Lot nr: Beads"
    )  # Post-PCR bead purification v1 process udf
    lot_nr_etoh_library_prep: str = Field(
        ..., alias="Lot nr: EtOH"
    )  # Post-PCR bead purification v1 process udf
    lot_nr_h2o_library_prep: str = Field(
        ..., alias="Lot nr: H2O"
    )  # Post-PCR bead purification v1 process udf
    finished_library_concentration: float = Field(
        ..., alias="Concentration"
    )  # aggregate qc men hämtas från denna: ??? : Post-PCR bead purification v1
    finished_library_concentration_nm: float = Field(
        ..., alias="Concentration (nM)"
    )  # aggregate qc men hämtas från denna: ??? : Post-PCR bead purification v1
    finished_library_size: Optional[float] = Field(
        ..., alias="Size (bp)"
    )  # aggregate qc men hämtas från denna: ??? : Post-PCR bead purification v1
    finished_library_average_size: float = Field(
        ..., alias="Average Size (bp)"
    )  # aggregate qc men hämtas från denna: ??? : Post-PCR bead purification v1
    lot_nr_dilution_buffer_library_normalization: Optional[str] = Field(
        ..., alias="Dilution buffer lot no"
    )  # CG002 - Normalization of microbial samples for sequencing process udf
    normalized_library_concentration: Optional[float] = Field(
        ..., alias="Final Concentration (nM)"
    )  # CG002 - Normalization of microbial samples for sequencing process udf
    library_normalization_method: Optional[str] = Field(
        ..., alias="Method document"
    )  # CG002 - Normalization of microbial samples for sequencing process udf


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
