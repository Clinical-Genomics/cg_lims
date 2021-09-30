from typing import Optional
from pydantic import Field, BaseModel
from cg_lims.objects import BaseAnalyte


class BeadPurificationArtifactUDFs(BaseModel):
    size_bp: Optional[str] = Field(None, alias="Size (bp)")
    concentration: Optional[str] = Field(None, alias="Concentration")


class BeadPurificationUDFs(BeadPurificationArtifactUDFs):
    class Config:
        allow_population_by_field_name = True


def get_bead_purification_twist(lims: Lims, sample_id: str) -> BeadPurificationUDFs:
    bead_purification_twist = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        artifact_udf_model=BeadPurificationArtifactUDFs,
        process_type="Bead Purification TWIST v2",
    )

    return BeadPurificationUDFs(**bead_purification_twist.merge_process_and_artifact_udfs())
