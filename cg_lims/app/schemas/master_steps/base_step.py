from genologics.lims import Lims
from pydantic import BaseModel


def get_artifact_udf(artifact, udf):
    if artifact:
        return artifact.udf.get(udf)
    return None


def get_process_udf(process, udf):
    if process:
        return process.udf.get(udf)
    return None


class BaseStep(BaseModel):
    sample_id: str
    lims: Lims

    class Config:
        arbitrary_types_allowed = True
