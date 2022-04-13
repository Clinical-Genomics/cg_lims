from typing import Optional

from genologics.lims import Lims
from pydantic import Field, BaseModel
from cg_lims.objects import BaseAnalyte
from cg_lims.models.arnold.base_step import BaseStep


class ArtifactUDFs(BaseModel):
    bead_purification_size_bp: Optional[int] = Field(None, alias="Size (bp)")
    bead_purification_concentration: Optional[float] = Field(None, alias="Concentration")


class ProcessUDFs(BaseModel):
    lot_nr_etoh_bead_purification_post_hyb: Optional[str] = Field(None, alias="Ethanol")
    lot_nr_h2o_bead_purification_post_hyb: Optional[str] = Field(None, alias="Nuclease free water")
    bead_purification_post_hyb_method: Optional[str] = Field(None, alias="Method document")
    binding_and_purification_beads: Optional[str] = Field(
        None, alias="Twist Binding and Purification beads"
    )


class ArnoldStep(BaseStep):
    artifact_udfs: ArtifactUDFs
    process_udfs: ProcessUDFs

    class Config:
        allow_population_by_field_name = True


def get_bead_purification_twist(lims: Lims, sample_id: str, prep_id: str) -> ArnoldStep:
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
        step_type="bead_purification",
        workflow="TWIST",
    )
