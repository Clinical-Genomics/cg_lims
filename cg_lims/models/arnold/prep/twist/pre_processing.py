from typing import Optional

from genologics.lims import Lims
from pydantic import Field, BaseModel

from cg_lims.objects import BaseAnalyte


class PreProcessingArtifactUDFs(BaseModel):
    pre_processing_concentration: Optional[str] = Field(None, alias="Concentration")


class PreProcessingUDFs(PreProcessingArtifactUDFs):
    pre_processing_well_position: Optional[str] = Field(None, alias="well_position")
    pre_processing_container_name: Optional[str] = Field(None, alias="container_name")

    class Config:
        allow_population_by_field_name = True


def get_pre_processing_twist(lims: Lims, sample_id: str) -> PreProcessingUDFs:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        artifact_udf_model=PreProcessingArtifactUDFs,
        optional_step=True,
    )

    return PreProcessingUDFs(
        **analyte.merge_analyte_fields(),
    )
