from typing import Optional

from genologics.lims import Lims
from pydantic import Field

from cg_lims.models.api.master_steps.base_step import BaseStep
from cg_lims.objects import BaseAnalyte


class PoolsamplesforhybridizationArtifactUDFs(BaseStep):
    amount_of_sample: Optional[str] = Field(None, alias="Total Amount (ng)")
    
    ""Kan man få fram hur många prov per pool det är?""


class PoolsamplesforhybridizationUDFs(PoolsamplesforhybridizationArtifactUDFs):
    class Config:
        allow_population_by_field_name = True


def get_pool_samples_twist(lims: Lims, sample_id: str) -> PoolsamplesforhybridizationUDFs:
    pool_samples_twist = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        artifact_udf_model=PoolsamplesforhybridizationArtifactUDFs,
        process_type="pool samples TWIST v2",
    )

    return PoolsamplesforhybridizationUDFs(**pool_samples_twist.merge_process_and_artifact_udfs())
