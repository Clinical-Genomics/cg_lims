from typing import Optional

from genologics.entities import Artifact, Process
from pydantic import Field, validator

from cg_lims.models.api.master_steps.base_step import get_artifact_udf, get_artifact_name, BaseStep
from cg_lims.get.artifacts import get_latest_analyte, get_artifacts


class PoolsamplesforhybridizationTWIST(BaseStep):
    "pool samples TWIST v2"
    artifact: Optional[Artifact]
    process: Optional[Process]
    amount_of_sample: Optional[str] = Field(None, alias="Total Amount (ng)")
    pool_name: Optional[str]

    @validator("artifact", always=True)
    def get_artifact(cls, v, values):
        try:
            return get_latest_analyte(
                lims=values.get("lims"),
                sample_id=values.get("sample_id"),
                process_types=["pool samples TWIST v2"],
            )
        except:
            return None

    @validator("process", always=True)
    def get_process(cls, v, values):
        if values.get("artifact"):
            return values.get("artifact").parent_process
        return None

    @validator("amount_of_sample", always=True)
    def get_amount_of_sample(cls, v, values):
        return get_artifact_udf(values.get("artifact"), "Total Amount (ng)")

    @validator("pool_name", always=True)
    def get_pool_name(cls, v, values):
        return get_artifact_name(values.get("artifact"))
