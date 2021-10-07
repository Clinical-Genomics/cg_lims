from typing import Optional

from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field
from cg_lims.objects import BaseAnalyte


class AliquotSamplesforCovarisArtifactUDF(BaseModel):
    sample_amount_needed: float = Field(..., alias="Amount needed (ng)")


class AliquotSamplesforCovarisUDF(AliquotSamplesforCovarisArtifactUDF):
    aliquotation_well_position: Optional[str] = Field(None, alias="well_position")
    aliquotation_container_name: Optional[str] = Field(None, alias="container_name")

    class Config:
        allow_population_by_field_name = True


def get_aliquot_samples_for_covaris_udfs(lims: Lims, sample_id: str) -> AliquotSamplesforCovarisUDF:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        artifact_udf_model=AliquotSamplesforCovarisArtifactUDF,
        process_type="Aliquot Samples for Covaris",
    )

    return AliquotSamplesforCovarisUDF(
        **analyte.merge_analyte_fields(),
    )
