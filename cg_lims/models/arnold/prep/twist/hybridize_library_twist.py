from typing import Optional

from genologics.lims import Lims
from pydantic import Field, BaseModel
from cg_lims.objects import BaseAnalyte
from cg_lims.models.arnold.base_step import BaseStep


class ArtifactUDFs(BaseModel):
    bait_set: Optional[str] = Field(None, alias="Bait Set")
    capture_kit: Optional[str] = Field(None, alias="Capture kit lot nr.")


class ProcessUDFs(BaseModel):
    lot_nr_blockers: Optional[str] = Field(None, alias="Blockers")
    lot_nr_hybridization_kit: Optional[str] = Field(None, alias="TWIST Hybridization kit")
    pcr_instrument_hybridization: Optional[str] = Field(None, alias="Thermal cycler (hyb)")
    hybridization_method: Optional[str] = Field(None, alias="Method document")


class ArnoldStep(BaseStep):
    process_udfs: ProcessUDFs
    artifact_udfs: ArtifactUDFs

    class Config:
        allow_population_by_field_name = True


def get_hybridize_library_twist(lims: Lims, sample_id: str, prep_id: str) -> ArnoldStep:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_type="Target enrichment TWIST v1",
    )

    return ArnoldStep(
        **analyte.base_fields(),
        process_udfs=ProcessUDFs(**analyte.process_udfs()),
        artifact_udfs=ArtifactUDFs(**analyte.artifact_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="hybridize_library",
        workflow="TWIST",
    )
