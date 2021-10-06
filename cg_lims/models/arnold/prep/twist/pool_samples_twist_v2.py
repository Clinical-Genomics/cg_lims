from typing import Optional

from genologics.lims import Lims
from pydantic import Field

from cg_lims.models.api.master_steps.base_step import BaseStep
from cg_lims.objects import BaseAnalyte


class PoolsamplesforhybridizationArtifactUDFs(BaseStep):
    amount_of_sample: Optional[str] = Field(None, alias="Total Amount (ng)")


class LibraryPreparationCovProcessUDFS(BaseModel):

    speedvac_temp: str = Field(..., alias="SpeedVac temp")
    speedvac_time: str = Field(..., alias="SpeedVac time (min)")


class PoolsamplesforhybridizationUDFs(PoolsamplesforhybridizationArtifactUDFs):
    # Number of samples in pools.
    class Config:
        allow_population_by_field_name = True


def get_pool_samples_twist(lims: Lims, sample_id: str) -> PoolsamplesforhybridizationUDFs:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        artifact_udf_model=PoolsamplesforhybridizationArtifactUDFs,
        process_type="pool samples TWIST v2",
    )

    return PoolsamplesforhybridizationUDFs(
        **analyte.merge_analyte_fields(),
    )
