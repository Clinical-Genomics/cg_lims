import logging
from collections import defaultdict
from typing import Dict, Optional

from genologics.entities import Artifact, Process
from genologics.lims import Lims

from cg_lims.exceptions import LimsError
from cg_lims.get.artifacts import get_lane_sample_artifacts
from cg_lims.get.fields import get_artifact_lims_id, get_flow_cell_name
from cg_lims.get.udfs import get_q30_threshold
from cg_lims.set.qc import set_quality_control_flag
from cg_lims.set.udfs import set_sample_q30_score, set_sample_reads

LOG = logging.getLogger(__name__)


class SampleArtifacts:
    """
    Responsible for easily storing and retrieving sample artifacts per sample id and lane.
    """

    def __init__(self):
        self._sample_artifacts: Dict[str, Dict[int, Artifact]] = defaultdict(dict)

    def add(self, artifact: Artifact, sample_id: str, lane: int) -> None:
        self._sample_artifacts[sample_id][lane] = artifact

    def get(self, sample_id: str, lane: int) -> Optional[Artifact]:
        return self._sample_artifacts.get(sample_id, {}).get(lane)


class SequencingArtifactManager:
    """
    Responsible for providing a high level interface for updating sample artifacts
    with sequencing metrics and retrieving the flow cell name and q30 threshold.
    """

    def __init__(self, process: Process, lims: Lims):
        self.process: Process = process
        self.lims: Lims = lims

        self._sample_artifacts: SampleArtifacts = SampleArtifacts()
        self._populate_sample_artifacts()

    def _populate_sample_artifacts(self) -> None:
        for lane, artifact in get_lane_sample_artifacts(self.process):
            sample_id: Optional[str] = get_artifact_lims_id(artifact)

            if not sample_id:
                LOG.warning(f"Failed to extract sample id from artifact: {artifact}")
                continue

            self._sample_artifacts.add(artifact=artifact, sample_id=sample_id, lane=lane)

    @property
    def flow_cell_name(self) -> str:
        flow_cell_name: Optional[str] = get_flow_cell_name(self.process)
        if not flow_cell_name:
            raise LimsError("Flow cell name not set")
        return flow_cell_name

    @property
    def q30_threshold(self) -> int:
        q30_threshold: Optional[int] = get_q30_threshold(self.process)
        if not q30_threshold:
            raise LimsError("Q30 threshold not set")
        return q30_threshold

    def update_sample(
        self,
        sample_lims_id: str,
        lane: int,
        reads: int,
        q30_score: float,
        passed_quality_control: bool,
    ) -> None:
        artifact: Optional[Artifact] = self._sample_artifacts.get(
            sample_id=sample_lims_id, lane=lane
        )

        if not artifact:
            LOG.warning(f"Sample artifact not found for {sample_lims_id} in lane {lane}. Skipping.")
            return

        set_sample_reads(sample_artifact=artifact, reads=reads)
        set_sample_q30_score(sample_artifact=artifact, q30_score=q30_score)
        set_quality_control_flag(artifact=artifact, passed=passed_quality_control)
        artifact.put()
