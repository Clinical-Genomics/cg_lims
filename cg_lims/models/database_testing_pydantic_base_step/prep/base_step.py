import logging

from genologics.lims import Lims, Process, Artifact

from cg_lims.get.artifacts import get_latest_artifact
from typing import Optional, Literal

from pydantic import BaseModel, Field
from pydantic import validator

from cg_lims.models.database.prep.microbial_prep import (
    LibraryPrepNexteraProcessUDFS,
)

LOG = logging.getLogger(__name__)


class BaseStep(BaseModel):
    sample_id: str
    process_type: str
    lims: Lims
    artifact: Optional[Artifact]
    process: Optional[Process]
    process_udf_model = Literal[LibraryPrepNexteraProcessUDFS]
    artifact_udf_model = Literal[LibraryPrepNexteraProcessUDFS]
    process_udfs: Optional[dict]
    artifact_udfs: Optional[dict]

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
        print(values)
        model = values.get("process_udf_model")
        print(model)
        if values.get("process"):
            udfs = dict(values.get("process").udf.items())
            return model(**udfs)
        return None

    @validator("artifact_udfs", always=True)
    def get_artifact_udfs(cls, v, values):
        model = values.get("artifact_udf_model")
        print(model)
        if values.get("artifact"):
            udfs = dict(values.get("artifact").udf.items())
            return model(**udfs)
        return None

    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True
