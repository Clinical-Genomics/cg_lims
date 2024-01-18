from typing import Optional

from cg_lims.models.arnold.base_step import BaseStep
from cg_lims.objects import BaseAnalyte
from genologics.lims import Lims
from pydantic.v1 import Field
from pydantic.v1.main import BaseModel


class SampleArtifactUDFs(BaseModel):
    """Aggregate QC (RNA) v1"""

    sample_rin: Optional[float] = Field(None, alias="RIN")
    sample_concentration: Optional[float] = Field(None, alias="Concentration")
    sample_amount: Optional[float] = Field(None, alias="Amount (ng)")


class SampleArtifactFields(BaseStep):
    artifact_udfs: SampleArtifactUDFs

    class Config:
        allow_population_by_field_name = True


def get_sample_artifact_fields(
    lims: Lims, sample_id: str, prep_id: str
) -> Optional[SampleArtifactFields]:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        optional_step=True,
    )
    sample_artifact_udfs = SampleArtifactUDFs(**analyte.artifact_udfs())
    if not sample_artifact_udfs.dict(exclude_none=True):
        return None

    return SampleArtifactFields(
        **analyte.base_fields(),
        artifact_udfs=sample_artifact_udfs,
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="reception_control",
        workflow="RNA"
    )
