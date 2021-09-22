import logging

from genologics.lims import Lims, Process, Artifact

from cg_lims.get.artifacts import get_latest_artifact
from typing import Optional

from pydantic import BaseModel
from pydantic import validator

LOG = logging.getLogger(__name__)


class BaseStep(BaseModel):
    sample_id: str
    process_type: str
    lims: Lims
    artifact: Optional[Artifact]
    process: Optional[Process]
    process_udfs: Optional[BaseModel]
    artifact_udfs: Optional[BaseModel]

    optional_step: bool = False

    @validator("artifact", always=True, pre=True)
    def get_artifact(cls, v, values):
        try:
            return get_latest_artifact(
                lims=values.get("lims"),
                sample_id=values.get("sample_id"),
                process_type=values.get("process_type"),
            )
        except:
            return None

    @validator("process", always=True)
    def get_process(cls, v, values):
        if values.get("artifact"):
            return values.get("artifact").parent_process
        return None

    @validator("process_udfs", always=True)
    def get_process_udfs(cls, v, values):
        if values.get("process"):
            udfs = dict(values.get("process").udf.items())
            return v(**udfs)
        return None

    @validator("artifact_udfs", always=True)
    def get_process_udfs(cls, v, values):
        if values.get("artifact"):
            udfs = dict(values.get("artifact").udf.items())
            return v(**udfs)
        return None
