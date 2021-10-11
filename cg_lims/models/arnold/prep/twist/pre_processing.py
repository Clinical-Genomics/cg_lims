from typing import Optional

from genologics.lims import Lims
from pydantic import Field, BaseModel

from cg_lims.objects import BaseAnalyte

from cg_lims.models.arnold.prep.base_step import BaseStep


class PreProcessingArtifactUDFs(BaseModel):
    pre_processing_concentration: Optional[str] = Field(None, alias="Concentration")


class PreProcessingFields(BaseStep):
    artifact_udfs: PreProcessingArtifactUDFs

    class Config:
        allow_population_by_field_name = True


def get_pre_processing_twist(lims: Lims, sample_id: str, prep_id: str) -> PreProcessingFields:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        optional_step=True,
    )

    return PreProcessingFields(
        **analyte.base_fields(),
        artifact_udfs=PreProcessingArtifactUDFs(**analyte.artifact_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="pre_processing",
        workflow="TWIST",
    )
