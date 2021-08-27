from typing import Optional

from genologics.entities import Artifact, Process
from pydantic import Field, validator

from cg_lims.models.api.master_steps.base_step import BaseStep, get_process_udf
from cg_lims.get.artifacts import get_latest_artifact


class CaptureandWashTWIST(BaseStep):
    "Capture and Wash TWIST v2"
    artifact: Optional[Artifact]
    process: Optional[Process]
    enrichment_kit: Optional[str] = Field(None, alias="Twist enrichment kit")
    hybridization_time: Optional[str] = Field(None, alias="Total hybridization time (h)")

    @validator("artifact", always=True)
    def get_artifact(cls, v, values):
        try:
            return get_latest_artifact(
                lims=values.get("lims"),
                sample_id=values.get("sample_id"),
                process_type=["Capture and Wash TWIST v2"],
            )
        except:
            return None

    @validator("process", always=True)
    def get_process(cls, v, values):
        if values.get("artifact"):
            return values.get("artifact").parent_process
        return None

    @validator("enrichment_kit", always=True)
    def get_enrichment_kit(cls, v, values):
        return get_process_udf(values.get("process"), "Twist enrichment kit")

    @validator("hybridization_time", always=True)
    def get_hybridization_time(cls, v, values):
        return get_process_udf(values.get("process"), "Total hybridization time (h)")
