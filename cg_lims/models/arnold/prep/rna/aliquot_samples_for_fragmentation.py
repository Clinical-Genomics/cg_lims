from typing import Optional

from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.objects import BaseAnalyte
from cg_lims.models.arnold.base_step import BaseStep


class ProcessUDFs(BaseModel):
    """Aliquot Samples for Fragmentation (RNA) v1"""

    poly_a_capture: Optional[str] = Field(None, alias="RGT no: Illumina PolyA capture")
    cdna_synthesis: Optional[str] = Field(None, alias="RGT no: Illumina cDNA synthesis")
    water: Optional[str] = Field(None, alias="Lot no: Nuclease free water")
    pcr_name: Optional[str] = Field(None, alias="Thermal cycler name")
    ampure_beads: Optional[str] = Field(None, alias="Lot no: AMPure XP-beads")
    et_oh: Optional[str] = Field(None, alias="Lot no: EtOH")


class ArtifactUDFs(BaseModel):
    volume_h2o: Optional[float] = Field(None, alias="Volume H2O (ul)")
    volume_sample: Optional[float] = Field(None, alias="Sample Volume (ul)")


class ArnoldStep(
    BaseStep,
):
    process_udfs: ProcessUDFs
    artifact_udfs: ArtifactUDFs

    class Config:
        allow_population_by_field_name = True


def get_aliquot_samples_for_enzymatic_fragmentation(
    lims: Lims, sample_id: str, prep_id: str
) -> ArnoldStep:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_type="Aliquot Samples for Fragmentation (RNA) v1",
    )

    return ArnoldStep(
        **analyte.base_fields(),
        process_udfs=ProcessUDFs(**analyte.process_udfs()),
        artifact_udfs=ArtifactUDFs(**analyte.artifact_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="aliquot_samples_for_fragmentation",
        workflow="RNA"
    )
