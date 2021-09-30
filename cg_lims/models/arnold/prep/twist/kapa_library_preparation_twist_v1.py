from typing import Optional
from genologics.lims import Lims
from pydantic import Field, BaseModel
from cg_lims.objects import BaseAnalyte


class KAPALibraryPreparationArtifactUDFs(BaseModel):
    size_bp: Optional[int] = Field(None, alias="Size (bp)")
    concentration: Optional[str] = Field(None, alias="Concentration")
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
    method_document: Optional[str] = Field(None, alias="Method document")
    document_version: Optional[int] = Field(None, alias="Document version")
    prep_kit: Optional[str] = Field(None, alias="KAPA HyperPlus/Prep Kit")


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
