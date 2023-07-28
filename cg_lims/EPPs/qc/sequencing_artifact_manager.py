import logging
from typing import Dict, Optional

from genologics.entities import Artifact, Process
from genologics.lims import Lims
from cg_lims.EPPs.files.sample_sheet.create_sample_sheet import get_lane_artifacts

from cg_lims.exceptions import LimsError
from cg_lims.get.fields import get_artifact_lims_id, get_flow_cell_name
from cg_lims.get.udfs import get_q30_threshold
from cg_lims.set.qc import set_quality_check_flag
from cg_lims.set.udfs import set_sample_q30_score, set_sample_reads

LOG = logging.getLogger(__name__)


class SampleArtifacts:
    def __init__(self):
        self._sample_artifacts: Dict[str, Dict[int, Artifact]] = {}

    def add(
        self, artifact: Artifact, lane: int
    ) -> None:
        sample_lims_id: Optional[str] = get_artifact_lims_id(artifact)

        if not lane or not sample_lims_id:
            LOG.warning(f"Failed to parse sample artifact: {artifact}")
            return
        
        if sample_lims_id not in self._sample_artifacts:
            self._sample_artifacts[sample_lims_id] = {}

        self._sample_artifacts[sample_lims_id][lane] = artifact

    def get(self, sample_lims_id: str, lane: int) -> Optional[Artifact]:
        return self._sample_artifacts.get(sample_lims_id, {}).get(lane)


class SequencingArtifactManager:
    def __init__(self, process: Process, lims: Lims):
        self.process: Process = process
        self.lims: Lims = lims

        self._sample_artifacts: SampleArtifacts = SampleArtifacts()
        self._set_sample_artifacts()

    def _set_sample_artifacts(self) -> None:
        lane_samples: Dict[int, Artifact] = get_lane_artifacts(self.process)

        for lane, artifact in lane_samples.items():
            self._sample_artifacts.add(artifact=artifact, lane=lane)

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
        sample_artifact: Optional[Artifact] = self._sample_artifacts.get(
            sample_lims_id=sample_lims_id, lane=lane
        )

        if not sample_artifact:
            LOG.warning(f"No metrics found for {sample_lims_id} in lane {lane}. Skipping.")
            return

        set_sample_reads(sample_artifact=sample_artifact, reads=reads)
        set_sample_q30_score(sample_artifact=sample_artifact, q30_score=q30_score)
        set_quality_check_flag(artifact=sample_artifact, quality_check_passed=passed_quality_control)

        sample_artifact.put()
