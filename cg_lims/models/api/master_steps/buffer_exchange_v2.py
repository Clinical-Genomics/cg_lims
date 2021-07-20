from typing import Optional

from genologics.entities import Artifact
from pydantic import Field, validator

from cg_lims.models.api.master_steps.base_step import get_artifact_udf, BaseStep
from cg_lims.get.artifacts import get_latest_artifact


class BufferExchange(BaseStep):
    artifact: Optional[Artifact]
    concentration: Optional[str] = Field(None, alias="Concentration")

    @validator("artifact", always=True)
    def get_artifact(cls, v, values):
        try:
            return get_latest_artifact(
                lims=values.get("lims"),
                sample_id=values.get("sample_id"),
                process_type=["Buffer Exchange v2"],
            )
        except:
            return None

    @validator("concentration", always=True)
    def get_size_bp(cls, v, values):
        return get_artifact_udf(values.get("artifact"), "Concentration")
