from typing import Optional

from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.objects import BaseAnalyte


<<<<<<< HEAD:cg_lims/models/arnold/prep/wgs/endrepair_size_selection_a_tailing_adapter_ligation.py
=======
        
class AliquotSamplesforCovarisArtifactUDF(BaseModel):        
    sample_amount_needed: float = Field(..., alias="Amount needed (ng)")

# well position (optional)
# container name (optional)
        
        
class FragmentDNATruSeqDNAProcessUDFS(BaseModel):        
    lot_nr_covaris_tube: str = Field(..., alias="Lot no: Covaris tube")
    fragmentation_method: str = Field(..., alias="Method Document 1")
    covaris_protocol: str = Field(..., alias="Protocol")
    lot_nr_resuspension_buffer_fragmentation: str = Field(..., alias="Lot no: Resuspension Buffer")
        
# well position (optional)
# container name (optional)
        
        
>>>>>>> 4e8eecb26563c9355817b989c6f843842f9d7137:cg_lims/models/arnold/prep/WGS.py
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
        
<<<<<<< HEAD:cg_lims/models/arnold/prep/wgs/endrepair_size_selection_a_tailing_adapter_ligation.py
  #  well_position_library_preparation: "well"
  #  plate_name_library_preparation: "Container Name"
=======
# well position (optional)
# container name (optional)
# index name

>>>>>>> 4e8eecb26563c9355817b989c6f843842f9d7137:cg_lims/models/arnold/prep/WGS.py
        
class EndrepairSizeselectionA_tailingandAdapterligationTruSeqPCR_freeDNAArtifactUDF(BaseModel):
    finished_library_concentration: Optional[float] = Field(None, alias="Concentration")
    finished_library_concentration_nm: float = Field(..., alias="Concentration (nM)")
    finished_library_size: Optional[float] = Field(None, alias="Size (bp)")
    


class EndrepairSizeselectionA_tailingandAdapterligationTruSeqPCR_freeUDFS(EndrepairSizeselectionA_tailingandAdapterligationTruSeqPCR_freeDNAProcessUDFS, EndrepairSizeselectionA_tailingandAdapterligationTruSeqPCR_freeDNAArtifactUDF):
    class Config:
        allow_population_by_field_name = True


def get_end_repair_udfs(lims: Lims, sample_id: str) -> EndrepairSizeselectionA_tailingandAdapterligationTruSeqPCR_freeUDFS:
    end_repair = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_udf_model=EndrepairSizeselectionA_tailingandAdapterligationTruSeqPCR_freeDNAProcessUDFS,
        artifact_udf_model=EndrepairSizeselectionA_tailingandAdapterligationTruSeqPCR_freeDNAArtifactUDF,
        process_type="Pooling and Clean-up (Cov) v1",
    )

    return EndrepairSizeselectionA_tailingandAdapterligationTruSeqPCR_freeUDFS(**end_repair.merge_process_and_artifact_udfs())
