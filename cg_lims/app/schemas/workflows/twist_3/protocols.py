from cg_lims.app.schemas.workflows.master_steps import *


class PreProcessingTWISTv2(BaseModel):
    """Pre Processing TWIST v2"""

    reception_control: Optional[ReceptionControlTWIST]
    buffer_exchanhge: Optional[BufferExchangeTWIST]


class InitialQCTWISTv3(BaseModel):
    """Initial QC TWIST v3"""

    tapestation_qc: Optional[TapestationReceptionControlTWIST]
    qubit_qc: Optional[QubitQCDNATWIST]
    quantit_qc: Optional[QuantitQCDNATWIST]
    aggregate_qc: Optional[AggregateQCDNATWIST]


class LibraryPrepTWISTv2(BaseModel):
    """Library Prep TWIST v2"""

    aliquot_samples: Optional[AliquotsamplesforenzymaticfragmentationTWIST]
    enzymatic_fragmentation: Optional[EnzymaticfragmentationTWIST]
    kapa_library_prep: Optional[KAPALibraryPreparation]


class LibraryValidationQCTWISTv2(BaseModel):
    """Library Validation QC TWIST v2"""

    tapestation_qc: Optional[TapestationQCTWIST]
    qubit_qc: Optional[QubitQCLibraryValidationTWIST]
    quantit_qc: Optional[QuantitQCLibraryValidationTWIST]
    aggregate_qc: Optional[AggregateQCLibraryValidationTWIST]


class TargetEnrichmentTWISTv2(BaseModel):
    """Target Enrichment TWIST v2"""

    pool_samples: Optional[PoolsamplesforhybridizationTWIST] = Field(
        None, alias="""pool samples TWIST v2"""
    )
    hybridize_library: Optional[HybridizeLibraryTWIST] = Field(
        None, alias="""Hybridize Library TWIST v2"""
    )
    capture_and_wash: Optional[CaptureandWashTWIST] = Field(
        None, alias="""Capture and Wash TWIST v2"""
    )
    amplify_captured_lib: Optional[AmplifyCapturedLibrariesTWIST] = Field(
        None, alias="""Amplify Captured Libraries TWIST v2"""
    )
    bead_purification: Optional[BeadPurificationTWIST] = Field(
        None, alias="""Bead Purification TWIST v2"""
    )
