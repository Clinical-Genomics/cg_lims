from typing import Optional

from genologics.lims import Lims
from pydantic import Field, validator, BaseModel
from cg_lims.objects import BaseAnalyte


class HybridizeLibraryTWISTArtifactUDFs(BaseModel):
    bait_set: Optional[str] = Field(None, alias="Bait Set")
    capture_kit: Optional[str] = Field(None, alias="Capture kit lot nr.")
    # container_name: Optional[str] = Field(None, alias="Container Name") How handle this...

    # @validator("container_name", always=True)
    # def get_container_name(cls, v, values):
    #    artifact = values.get("artifact")
    #    if artifact:
    #        return artifact.container.name
    #    return None


class HybridizeLibraryTWISTProcessUDFs(BaseModel):
    lot_nr_enrichment_kit_hybridization: Optional[str] = Field(None, alias="Twist enrichment kit")
    lot_nr_blockers: str = Field(..., alias="Blockers")
    lot_nr_hybridization_kit: str = Field(..., alias="TWIST Hybridization kit")
    lot_nr_vapor_lock: str = Field(..., alias="Vapor lock")
    pcr_instrument_hybridization: str = Field(..., alias="Thermal cycler")
    hybridization_method: str = Field(..., alias="Method document")
        
# well position (optional)
# container name (optional)


class HybridizeLibraryUDFs(HybridizeLibraryTWISTArtifactUDFs, HybridizeLibraryTWISTProcessUDFs):
    class Config:
        allow_population_by_field_name = True


def get_hybridize_library_twist(lims: Lims, sample_id: str) -> HybridizeLibraryUDFs:
    _hybridize_library_twist = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        artifact_udf_model=HybridizeLibraryTWISTArtifactUDFs,
        process_udf_model=HybridizeLibraryTWISTProcessUDFs,
        process_type="Hybridize Library TWIST v2",
    )

    return HybridizeLibraryUDFs(**_hybridize_library_twist.merge_process_and_artifact_udfs())
