from typing import Optional

from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.objects import BaseAnalyte

from cg_lims.models.arnold.base_step import BaseStep


class SampleArtifactUDF(BaseModel):
    sample_concentration: Optional[float] = Field(None, alias="Concentration")
    sample_amount: Optional[float] = Field(None, alias="Amount (ng)")


class SampleArtifactFields(BaseStep):
    artifact_udfs: SampleArtifactUDF

    class Config:
        allow_population_by_field_name = True


def get_sample_artifact_fields(lims: Lims, sample_id: str, prep_id: str) -> SampleArtifactFields:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
    )

    return SampleArtifactFields(
        **analyte.base_fields(),
        artifact_udfs=SampleArtifactUDF(**analyte.artifact_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="reception_control",
        workflow="WGS"
    )
