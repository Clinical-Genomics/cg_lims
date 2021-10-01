from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field
from cg_lims.objects import BaseAnalyte


class AliquotSamplesforCovarisArtifactUDF(BaseModel):
    sample_amount_needed: float = Field(..., alias="Amount needed (ng)")


class AliquotSamplesforCovarisUDF(AliquotSamplesforCovarisArtifactUDF):
    class Config:
        allow_population_by_field_name = True


def get_aliquot_samples_for_covaris_udfs(lims: Lims, sample_id: str) -> AliquotSamplesforCovarisUDF:
    aliquot_samples_for_covaris = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        artifact_udf_model=AliquotSamplesforCovarisArtifactUDF,
        process_type="Pooling and Clean-up (Cov) v1",
    )

    return AliquotSamplesforCovarisUDF(**aliquot_samples_for_covaris.merge_process_and_artifact_udfs())
