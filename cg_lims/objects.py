"""Base cg_lims calss definitions
"""
from typing import Optional

from genologics.entities import Artifact, Sample
from genologics.lims import Lims

from cg_lims.exceptions import (
    MissingUDFsError,
    ZeroReadsError,
    MissingArtifactError,
    MissingProcessError,
)
from cg_lims.get.artifacts import get_sample_artifact, get_latest_artifact
import logging

LOG = logging.getLogger(__name__)


class Pool:
    """Collecting informatiuon general to any pool"""

    def __init__(self, pool_artifact: Artifact):
        self.total_reads_missing = 0
        self.artifact = pool_artifact

    def get_total_reads_missing(self) -> None:
        """Get the total numer of missing reads in the pool"""

        for art in self.artifact.input_artifact_list():
            reads = art.samples[0].udf.get("Reads missing (M)")
            if reads is None:
                raise MissingUDFsError("Missing udfs: Reads missing (M)")
            self.total_reads_missing += reads
        if self.total_reads_missing == 0:
            raise ZeroReadsError("All samples seem to have Missing Reads = 0!")


class BaseAnalyte:
    """This class defines a Analyte by:

    sample_id: The submitted sample from which the analyte is derived.
    process_type: The process in which the analyte was generated (the artifact.parent_process).
                  If process_type is None, then the analyte is the original submitted sample.
    artifact_udf_model: Defines the analyte udfs.
    process_udf_model: Defines the parent process udfs.
    """

    def __init__(
        self,
        lims: Lims,
        sample_id: str,
        process_type: str = None,
        artifact_udf_model=None,
        process_udf_model=None,
        optional_step: bool = False,
    ):
        self.lims: Lims = lims
        self.sample_id: str = sample_id
        self.process_type: str = process_type
        self.artifact_udf_model = artifact_udf_model
        self.process_udf_model = process_udf_model
        self.optional_step: bool = optional_step
        self.artifact: Optional[Artifact] = self.get_artifact()

    def get_artifact(self) -> Optional[Artifact]:
        """Getting the analyte artifact based on sample_id and process_type.
        If process_type is None, then the analyte is the original submitted sample."""
        if not self.process_type:
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
        """Filtering process udfs by process_udf_model."""
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
        """Filtering artifact udfs by artifact_udf_model."""
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
        """Merging process and artifact udfs into one dict."""

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
