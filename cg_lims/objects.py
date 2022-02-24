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
        """Get the total number of missing reads in the pool"""

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
    process_types: The process in which the analyte was generated (the artifact.parent_process).
                  If process_types is None, then the analyte is the original submitted sample.
    """

    def __init__(
        self,
        lims: Lims,
        sample_id: str,
        process_type: str = None,
        optional_step: bool = False,
    ):
        self.lims: Lims = lims
        self.sample_id: str = sample_id
        self.process_type: str = process_type
        self.optional_step: bool = optional_step
        self.artifact: Optional[Artifact] = self.get_artifact()

    def get_well(self) -> Optional[str]:
        """Returning artifact well if existing."""
        if not (self.artifact and self.artifact.location and self.artifact.location[1] != "1:1"):
            return None
        return self.artifact.location[1]

    def get_container_name(self) -> Optional[str]:
        """Returning artifact container name if existing."""
        if not (self.artifact and self.artifact.container and self.artifact.container.name):
            return None
        return self.artifact.container.name

    def get_container_id(self) -> Optional[str]:
        """Returning artifact container id if existing."""
        if not (self.artifact and self.artifact.container and self.artifact.container.id):
            return None
        return self.artifact.container.id

    def get_container_type(self) -> Optional[str]:
        """Returning artifact container type if existing."""
        if not (self.artifact and self.artifact.container and self.artifact.container.type):
            return None
        return self.artifact.container.type.name

    def get_index(self) -> Optional[str]:
        """Returning artifact index if existing."""
        if not (
            self.artifact
            and self.artifact.reagent_labels
            and len(self.artifact.reagent_labels) == 1
        ):
            return None
        return self.artifact.reagent_labels[0]

    def get_nr_samples(self) -> Optional[int]:
        """Returning nr samples in pool if existing."""
        if not (self.artifact and self.artifact.samples and len(self.artifact.samples) > 1):
            return None
        return len(self.artifact.samples)

    def get_artifact_name(self) -> Optional[int]:
        """Returning artifact name if existing."""
        if not self.artifact:
            return None
        return self.artifact.name

    def get_artifact(self) -> Optional[Artifact]:
        """Getting the analyte artifact based on sample_id and process_types.
        If process_types is None, then the analyte is the original submitted sample."""
        if not self.process_type:
            sample = Sample(self.lims, id=self.sample_id)
            return get_sample_artifact(sample=sample, lims=self.lims)
        try:
            return get_latest_artifact(
                lims=self.lims, sample_id=self.sample_id, process_types=[self.process_type]
            )
        except MissingArtifactError as e:
            LOG.info(e.message)
            if self.optional_step:
                return None
            raise e

    def get_date(self):
        """Date when artifact was produced."""
        if not (
            self.artifact and self.artifact.parent_process and self.artifact.parent_process.date_run
        ):
            return None

        return self.artifact.parent_process.date_run

    def process_udfs(self) -> dict:
        """Filtering process udfs by process_udf_model."""
        if self.artifact and self.artifact.parent_process:
            return dict(self.artifact.parent_process.udf.items())

        if self.optional_step:
            return {}

        raise MissingProcessError(
            message=f"sample didnt pass through requiered process {self.process_type}"
        )

    def artifact_udfs(self) -> dict:
        """Filtering artifact udfs by artifact_udf_model."""
        if self.artifact:
            return dict(self.artifact.udf.items())
        if self.optional_step:
            return {}
        raise MissingProcessError(
            message=f"sample didnt pass through requiered process {self.process_type}"
        )

    def base_fields(self) -> dict:

        return dict(
            well_position=self.get_well(),
            container_name=self.get_container_name(),
            container_id=self.get_container_id(),
            container_type=self.get_container_type(),
            index_name=self.get_index(),
            nr_samples_in_pool=self.get_nr_samples(),
            artifact_name=self.get_artifact_name(),
            lims_step_name=self.process_type,
            date_run=self.get_date(),
        )
