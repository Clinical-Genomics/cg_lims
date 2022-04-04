from typing import Optional

from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.models.arnold.base_step import BaseStep
from cg_lims.objects import BaseAnalyte


class ProcessUDFs(BaseModel):
    """Xp Denature & ExAmp (Nova Seq)"""

    dpx1_volume: Optional[str] = Field(None, alias="DPX1 Volume (ul)")
    dpx2_volume: Optional[str] = Field(None, alias="DPX2 Volume (ul)")
    dpx3_volume: Optional[str] = Field(None, alias="DPX3 Volume (ul)")
    tris_lot_nr: Optional[str] = Field(None, alias="Tris-HCl lot nr")
    naoh_lot_nr: Optional[str] = Field(None, alias="NaOH lot nr")
    phix_lot_nr: Optional[str] = Field(None, alias="PhiX lot nr")
    examp_lot_nr: Optional[str] = Field(None, alias="ExAmp lot nr")


class ArtifactUDFs(BaseModel):
    bp_aliquot_volume: Optional[float] = Field(None, alias="BP Aliquot Volume (ul)")
    naoh_volume: Optional[float] = Field(None, alias="NaOH Volume (ul)")
    tris_volume: Optional[float] = Field(None, alias="Tris-HCl Volume (ul)")
    phix_volume: Optional[float] = Field(None, alias="PhiX Volume (ul)")
    mastermix_per_lane: Optional[float] = Field(None, alias="Mastermix per Lane (ul)")


class ArnoldStep(BaseStep):
    process_udfs: ProcessUDFs
    artifact_udfs: ArtifactUDFs

    class Config:
        allow_population_by_field_name = True


def get_xp_denature_and_examp(lims: Lims, sample_id: str, prep_id: str) -> Optional[ArnoldStep]:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_type="Xp Denature & ExAmp (Nova Seq)",
        optional_step=True,
    )
    if not analyte.process:
        return None
    return ArnoldStep(
        **analyte.base_fields(),
        process_udfs=ProcessUDFs(**analyte.process_udfs()),
        artifact_udfs=ArtifactUDFs(**analyte.artifact_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="xp_denature_and_examp",
        workflow="NovaSeq"
    )
