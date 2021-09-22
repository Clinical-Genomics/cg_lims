import logging

from genologics.lims import Lims, Artifact, Sample

from cg_lims.exceptions import MissingArtifactError, MissingProcessError
from cg_lims.get.artifacts import get_latest_artifact, get_sample_artifact
from typing import Optional


LOG = logging.getLogger(__name__)


class BaseStep:
    def __init__(
        self,
        lims: Lims,
        sample_id: str,
        process_type: str,
        artifact_udf_model=None,
        process_udf_model=None,
        optional_step: bool = False,
        sample_artifact: bool = False,
    ):
        self.lims: Lims = lims
        self.sample_id: str = sample_id
        self.process_type: str = process_type
        self.artifact_udf_model = artifact_udf_model
        self.process_udf_model = process_udf_model
        self.optional_step: bool = optional_step
        self.sample_artifact: bool = sample_artifact
        self.artifact: Optional[Artifact] = self.get_artifact()

    def get_artifact(self) -> Optional[Artifact]:
        if self.sample_artifact:
            sample = Sample(self.lims, id=self.sample_id)
            return get_sample_artifact(sample=sample, lims=self.lims)
        try:
            return get_latest_artifact(
                lims=self.lims, sample_id=self.sample_id, process_type=[self.process_type]
            )
        except MissingArtifactError as e:
            LOG.info(e.message)
            if self.optional_step:
                return None
            raise e

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

    def merge_process_and_artifact_udfs(self) -> dict:
        """"""

        if not self.artifact:
            return {}
        if self.process_udf_model:
            process_udfs: dict = self.filter_process_udfs_by_model()
        else:
            process_udfs = {}
        if self.artifact_udf_model:
            artifact_udfs: dict = self.filter_artifact_udfs_by_model()
        else:
            artifact_udfs = {}
        merged_udfs = {}
        merged_udfs.update(process_udfs)
        merged_udfs.update(artifact_udfs)
        return merged_udfs
