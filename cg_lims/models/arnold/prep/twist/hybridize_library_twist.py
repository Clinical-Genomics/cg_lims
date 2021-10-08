from typing import Optional

from genologics.lims import Lims
from pydantic import Field, BaseModel
from cg_lims.objects import BaseAnalyte
from cg_lims.models.arnold.prep.base_step import BaseStep


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


class HybridizeLibraryFields(BaseStep):
    process_udfs: HybridizeLibraryTWISTProcessUDFs
    artifact_udfs: HybridizeLibraryTWISTArtifactUDFs

    class Config:
        allow_population_by_field_name = True


def get_hybridize_library_twist(lims: Lims, sample_id: str, prep_id: str) -> HybridizeLibraryFields:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_type="Hybridize Library TWIST v2",
    )

    return HybridizeLibraryFields(
        **analyte.base_fields(),
        process_udfs=HybridizeLibraryTWISTProcessUDFs(**analyte.process_udfs()),
        artifact_udfs=HybridizeLibraryTWISTArtifactUDFs(**analyte.artifact_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="hybridize_library",
        workflow="TWIST",
    )
