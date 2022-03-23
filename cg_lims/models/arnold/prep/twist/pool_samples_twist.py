from typing import Optional
from genologics.lims import Lims
from pydantic import Field, BaseModel
from cg_lims.objects import BaseAnalyte

from cg_lims.models.arnold.prep.base_step import BaseStep


class ArtifactUDFs(BaseModel):
    amount_of_sample: Optional[float] = Field(None, alias="Total Amount (ng)")


class ProcessUDFs(BaseModel):

    speedvac_temp: Optional[float] = Field(None, alias="SpeedVac temp")
    speedvac_time: Optional[float] = Field(None, alias="SpeedVac time (min)")


class ArnoldStep(BaseStep):
    process_udfs: ProcessUDFs
    artifact_udfs: ArtifactUDFs
    #!!! same as container_name??? https://clinical-lims.scilifelab.se/clarity/work-complete/159432  Optional[str] = Field(None, alias="container_name")

    class Config:
        allow_population_by_field_name = True


def get_pool_samples_twist(lims: Lims, sample_id: str, prep_id: str) -> ArnoldStep:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_type="pool samples TWIST v2",
    )

    return ArnoldStep(
        **analyte.base_fields(),
        process_udfs=ProcessUDFs(**analyte.process_udfs()),
        artifact_udfs=ArtifactUDFs(**analyte.artifact_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="pool_samples",
        workflow="TWIST",
    )
