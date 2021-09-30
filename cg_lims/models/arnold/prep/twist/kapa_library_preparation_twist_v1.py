from typing import Optional
from genologics.lims import Lims
from pydantic import Field, BaseModel
from cg_lims.objects import BaseAnalyte


class KAPALibraryPreparationArtifactUDFs(BaseModel):
    library_size_pre_hyb: str = Field(..., alias="Size (bp)")
    library_concentration_pre_hyb: str = Field(..., alias="Concentration")
    adapter_ligation_master_mix: str = Field(..., alias="Ligation Master Mix")
    library_preparation_pcr_plate: str = Field(..., alias="PCR Plate")
        
        
    # label: Optional[str] = Field(None, alias="label (= index)")
    # well: Optional[str] = Field(None, alias="Well")
    # container_name: Optional[str] = Field(None, alias="Container Name")


# @validator("container_name", always=True)
# def get_container_name(cls, v, values):
#    artifact = values.get("artifact")
#    if artifact:
#        return artifact.container.name
#    return None

# @validator("well", always=True)
# def get_well(cls, v, values):
#    artifact = values.get("artifact")
#    if artifact:
#        return artifact.location[1]
#    return None

# @validator("label", always=True)
# def get_kapa_label(cls, v, values):
#    artifact = values.get("artifact")
#    if artifact:
#        return artifact.reagent_labels
#    return None


class KAPALibraryPreparationProcessUDFs(BaseModel):
    method_document_library_preparation: str = Field(..., alias="Method document")   
    library_preparation_kit: str = Field(..., alias="KAPA HyperPlus/Prep Kit")
    lot_nr_h2o_library_preparation_pre_lab: str = Field(..., alias="Nuclease-free water (pre-lab)")
    lot_nr_xgen_adapter: str = Field(..., alias="xGen Adapter")
    lot_nr_index: str = Field(..., alias="Indexing Primer")
    lot_nr_beads_library_preparation_pre_lab: str = Field(..., alias="DNA purification beads (pre-lab)")
    lot_nr_etoh_library_preparation_pre_lab: str = Field(..., alias="Ethanol (pre-lab)")
    pcr_instrument_end_repair_a_tail: str = Field(..., alias="PCR Machine: End Repair and A-tail")
    pcr_instrument_adapter_ligation: str = Field(..., alias="PCR Machine: Adapter ligation")
    pcr_instrument_amplification_plate1: Optional[str] = Field(None, alias="PCR Machine: Amplification Plate 1")
    pcr_instrument_amplification_plate2: Optional[str] = Field(None, alias="PCR Machine: Amplification Plate 2")
    pcr_instrument_amplification_plate3: Optional[str] = Field(None, alias="PCR Machine: Amplification Plate 3")
    lot_nr_beads_library_preparation_post_lab: str = Field(..., alias="DNA purification beads (post-lab)")
    lot_nr_etoh_library_preparation_post_lab: str = Field(..., alias="Ethanol (post-lab)")    
    lot_nr_h2o_library_preparation_post_lab: str = Field(..., alias="Nuclease-free water (post-lab)")
        
        ""Kan även vara bra att ta med label groups (dvs index set)""
        
        


class KAPALibraryPreparationUDFs(
    KAPALibraryPreparationProcessUDFs, KAPALibraryPreparationArtifactUDFs
):
    class Config:
        allow_population_by_field_name = True


def get_kapa_library_preparation_twist(lims: Lims, sample_id: str) -> KAPALibraryPreparationUDFs:
    kapa_library_preparation_twist = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        artifact_udf_model=KAPALibraryPreparationArtifactUDFs,
        process_udf_model=KAPALibraryPreparationProcessUDFs,
        process_type="KAPA Library Preparation TWIST v1",
    )

    return KAPALibraryPreparationUDFs(
        **kapa_library_preparation_twist.merge_process_and_artifact_udfs()
    )
