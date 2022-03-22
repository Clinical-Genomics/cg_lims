from typing import Optional

from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field
from cg_lims.objects import BaseAnalyte
from cg_lims.models.arnold.prep.base_step import BaseStep


class ArtifactUDF(BaseModel):
    sample_amount_needed: Optional[float] = Field(None, alias="Amount needed (ng)")


class ArnoldStep(BaseStep):
    artifact_udfs: ArtifactUDF

    class Config:
        allow_population_by_field_name = True


def get_aliquot_samples_for_covaris(lims: Lims, sample_id: str, prep_id: str) -> ArnoldStep:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_type="Aliquot Samples for Covaris",
    )

    return ArnoldStep(
        **analyte.base_fields(),
        artifact_udfs=ArtifactUDF(**analyte.artifact_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="aliquot_samples_for_covaris",
        workflow="WGS",
    )
