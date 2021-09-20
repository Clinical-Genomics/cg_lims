import logging

from genologics.lims import Lims, Process, Artifact

from cg_lims.exceptions import MissingArtifactError, MissingProcessError
from cg_lims.get.artifacts import get_latest_artifact
from typing import Optional

from pydantic import Field, BaseModel

LOG = logging.getLogger(__name__)


class BasePrep:
    def __init__(self, lims: Lims, sample_id: str):
        self.lims = lims
        self.sample_id = sample_id
        self.process_type = None
        self.artifact_udf_model = None
        self.process_udf_model = None
        self.artifact = None
        self.optional_step = False

    def set_artifact(self) -> Optional[Artifact]:
        try:
            return get_latest_artifact(
                lims=self.lims, sample_id=self.sample_id, process_type=[self.process_type]
            )
        except MissingArtifactError as e:
            LOG.info(e.message)
            return None

    def set_process(self) -> Optional[Process]:
        try:
            return self.artifact.parent_process()
        except MissingProcessError as e:
            LOG.info(e.message)
            return None

    def filter_process_udfs_by_model(self) -> dict:
        """"""

        try:
            process_udfs = dict(self.artifact.parent_process.udf.items())
        except:
            if self.optional_step:
                return {}
            raise MissingProcessError(
                message=f"sample didnt pass through requiered process {self.process_type}"
            )
        udf_model = self.process_udf_model(**process_udfs)
        return udf_model.dict(exclude_none=True)

    def filter_artifact_udfs_by_model(self) -> dict:
        """"""
        try:
            artifact_udfs = dict(self.artifact.udf.items())
        except:
            if self.optional_step:
                return {}
            raise MissingProcessError(
                message=f"sample didnt pass through requiered process {self.process_type}"
            )
        udf_model = self.artifact_udf_model(**artifact_udfs)
        return udf_model.dict(exclude_none=True)


class Prep(BaseModel):
    """LIMS Prep Collection"""

    id: Optional[str] = Field(..., alias="_id")
    prep_id: str
    sample_id: str
    workflow: str
