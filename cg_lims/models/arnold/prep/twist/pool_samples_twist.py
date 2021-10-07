from typing import Optional
from genologics.lims import Lims
from pydantic import Field, BaseModel
from cg_lims.objects import BaseAnalyte


class PoolsamplesforhybridizationArtifactUDFs(BaseModel):
    amount_of_sample: Optional[str] = Field(None, alias="Total Amount (ng)")


class PoolsamplesforhybridizationProcessUDFs(BaseModel):

    speedvac_temp: str = Field(..., alias="SpeedVac temp")
    speedvac_time: str = Field(..., alias="SpeedVac time (min)")


class PoolsamplesforhybridizationUDFs(
    PoolsamplesforhybridizationArtifactUDFs, PoolsamplesforhybridizationProcessUDFs
):
    pool_nr_samples: Optional[int] = Field(None, alias="nr_samples")
    pool_name: Optional[str] = Field(None, alias="container_name")
    #!!! same as container_name??? https://clinical-lims.scilifelab.se/clarity/work-complete/159432  Optional[str] = Field(None, alias="container_name")

    class Config:
        allow_population_by_field_name = True


def get_pool_samples_twist(lims: Lims, sample_id: str) -> PoolsamplesforhybridizationUDFs:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        artifact_udf_model=PoolsamplesforhybridizationArtifactUDFs,
        process_udf_model=PoolsamplesforhybridizationProcessUDFs,
        process_type="pool samples TWIST v2",
    )

    return PoolsamplesforhybridizationUDFs(
        **analyte.merge_analyte_fields(),
    )
