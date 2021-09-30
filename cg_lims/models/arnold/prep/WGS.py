from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.objects import BaseAnalyte

""Från protocol Initial QC wgs v4:""
class InitialQCwgsv4ArtifactUDF(BaseModel):
    sample_concentration: float = Field(..., alias="Concentration")
    sample_amount: float = Field(..., alias="Amount (ng)")
    sample_priority: float = Field(..., alias="priority")

        
class AliquotSamplesforCovarisArtifactUDF(BaseModel):        
    sample_amount_needed: float = Field(..., alias="Amount needed (ng)")
        
        
class FragmentDNATruSeqDNAProcessUDFS(BaseModel):        
    lot_nr_covaris_tube: str = Field(..., alias="Lot no: Covaris tube")
    fragmentation_method: str = Field(..., alias="Method Document 1")
    covaris_protocol: str = Field(..., alias="Protocol")
    lot_nr_resuspension_buffer_fragmentation: str = Field(..., alias="Lot no: Resuspension Buffer")
        
        
class EndrepairSizeselectionA_tailingandAdapterligationTruSeqPCR_freeDNAProcessUDFS(BaseModel):
    lot_nr_truseq_library_preparation_kit: Optional[float] = Field(None, alias="Lot no: TruSeq DNA PCR-Free Sample Prep Kit")
    lot_nr_index: str = Field(..., alias="Lot no: Adaptor Plate")
    lot_nr_beads: str = Field(..., alias="Lot no: SP Beads")
    lot_nr_lucigen_library_preparation_kit: Optional[float] = Field(None, alias="Lot no: Lucigen prep kit")
    pcr_instrument_incubation: str = Field(..., alias="PCR machine")
    lot_nr_h2o_library_preparation: str = Field(..., alias="Lot no: Nuclease free water")
    lot_nr_resuspension_buffer_library_preparation: str = Field(..., alias="Lot no: Resuspension buffer")
    library_preparation_method: str = Field(..., alias="Method document")
    lot_nr_etoh_library_preparation: str = Field(..., alias="Ethanol lot")
        
class EndrepairSizeselectionA_tailingandAdapterligationTruSeqPCR_freeDNAArtifactUDF(BaseModel):
    finished_library_concentration: Optional[float] = Field(None, alias="Concentration")
    finished_library_concentration_nm: float = Field(..., alias="Concentration (nM)")
    finished_library_size: Optional[float] = Field(None, alias="Size (bp)")
    
