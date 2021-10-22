from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field
from cg_lims.objects import BaseAnalyte
from cg_lims.models.arnold.prep.base_step import BaseStep


class AliquotSamplesforCovarisArtifactUDF(BaseModel):
    sample_amount_needed: float = Field(..., alias="Amount needed (ng)")


class AliquotSamplesforCovarisFields(BaseStep):
    artifact_udfs: AliquotSamplesforCovarisArtifactUDF

    class Config:
        allow_population_by_field_name = True


def get_aliquot_samples_for_covaris(
    lims: Lims, sample_id: str, prep_id: str
) -> AliquotSamplesforCovarisFields:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_type="Aliquot Samples for Covaris",
    )

    return AliquotSamplesforCovarisFields(
        **analyte.base_fields(),
        artifact_udfs=AliquotSamplesforCovarisArtifactUDF(**analyte.artifact_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="aliquot_samples_for_covaris",
        workflow="WGS",
    )
