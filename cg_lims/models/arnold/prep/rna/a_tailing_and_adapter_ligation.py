from typing import Optional

from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.objects import BaseAnalyte
from cg_lims.models.arnold.prep.base_step import BaseStep


class ProcessUDFs(BaseModel):
    """A-tailing and Adapter ligation (RNA) v1"""

    rna_prepp: Optional[str] = Field(None, alias="RGT no: Illumina RNAprep")
    rna_index_anchors: Optional[str] = Field(None, alias="Lot no: RNA index anchors")
    index: Optional[str] = Field(None, alias="Lot no: Index")
    pcr_pre_lab: Optional[str] = Field(None, alias="Thermal cycler (pre-lab)")
    water_pre_lab: Optional[str] = Field(None, alias="Lot no: Nuclease-free water (pre-lab)")
    et_oh_pre_lab: Optional[str] = Field(None, alias="Lot no: EtOH (pre-lab)")
    ampure_beads_pre_lab: Optional[str] = Field(None, alias="Lot no: AMPure XP-beads (pre-lab)")
    pcr_amplification: Optional[str] = Field(None, alias="Thermal cycler Amplification")
    cycles_pcr: int = Field(..., alias="Number of PCR cycles used")
    ampure_beads_post_lab: Optional[str] = Field(None, alias="Lot no: AMPure XP-beads (post-lab)")
    et_oh_post_lab: Optional[str] = Field(None, alias="Lot no: EtOH (post-lab)")
    water_post_lab: Optional[str] = Field(None, alias="Lot no: Nuclease-free water (post-lab)")
    resuspension_buffer_post_lab: Optional[str] = Field(
        None, alias="Lot no: Resuspension buffer (post-lab)"
    )


class ArtifactUDFs(BaseModel):
    concentration: Optional[float] = Field(None, alias="Concentration")
    size: Optional[int] = Field(None, alias="Size (bp)")


class ArnoldStep(
    BaseStep,
):
    artifact_udfs: ArtifactUDFs
    process_udfs: ProcessUDFs

    class Config:
        allow_population_by_field_name = True


def get_a_tailning_and_adapter_ligation(lims: Lims, sample_id: str, prep_id: str) -> ArnoldStep:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_type="A-tailing and Adapter ligation (RNA) v1",
    )

    return ArnoldStep(
        **analyte.base_fields(),
        process_udfs=ProcessUDFs(**analyte.process_udfs()),
        artifact_udfs=ArtifactUDFs(**analyte.artifact_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="a_tailing_and_adapter_ligation",
        workflow="RNA"
    )
