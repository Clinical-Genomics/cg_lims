from typing import Optional

from genologics.lims import Lims
from pydantic import Field, BaseModel
from cg_lims.objects import BaseAnalyte


class HybridizeLibraryTWISTArtifactUDFs(BaseModel):
    bait_set: Optional[str] = Field(None, alias="Bait Set")
    capture_kit: Optional[str] = Field(None, alias="Capture kit lot nr.")


class HybridizeLibraryTWISTProcessUDFs(BaseModel):
    lot_nr_enrichment_kit_hybridization: Optional[str] = Field(None, alias="Twist enrichment kit")
    lot_nr_blockers: str = Field(..., alias="Blockers")
    lot_nr_hybridization_kit: str = Field(..., alias="TWIST Hybridization kit")
    lot_nr_vapor_lock: str = Field(..., alias="Vapor lock")
    pcr_instrument_hybridization: str = Field(..., alias="Thermal cycler")
    hybridization_method: str = Field(..., alias="Method document")


class HybridizeLibraryUDFs(HybridizeLibraryTWISTArtifactUDFs, HybridizeLibraryTWISTProcessUDFs):
    hybridization_well_position: Optional[str] = Field(None, alias="well_position")
    hybridization_container_name: Optional[str] = Field(None, alias="container_name")

    class Config:
        allow_population_by_field_name = True


def get_hybridize_library_twist(lims: Lims, sample_id: str) -> HybridizeLibraryUDFs:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        artifact_udf_model=HybridizeLibraryTWISTArtifactUDFs,
        process_udf_model=HybridizeLibraryTWISTProcessUDFs,
        process_type="Hybridize Library TWIST v2",
    )

    return HybridizeLibraryUDFs(
        **analyte.merge_analyte_fields(),
    )
