import logging
from typing import Dict, List, Optional

from genologics.entities import Artifact, Process
from genologics.lims import Lims

from cg_lims.EPPs.files.sample_sheet.create_sample_sheet import get_artifact_lane
from cg_lims.exceptions import LimsError
from cg_lims.get.artifacts import get_sample_artifacts
from cg_lims.get.fields import get_artifact_lims_id, get_flow_cell_name
from cg_lims.get.udfs import get_q30_threshold
from cg_lims.set.qc import set_quality_check_flag
from cg_lims.set.udfs import set_sample_q30_score, set_sample_reads

LOG = logging.getLogger(__name__)


class SequencingArtifactManager:
    def __init__(self, process: Process, lims: Lims):
        self.process: Process = process
        self.lims: Lims = lims

        self.sample_artifacts: Dict[str, Dict[int, Artifact]] = {}
        self._set_sample_artifacts()

    def _set_sample_artifacts(self) -> None:
        sample_artifacts: List[Artifact] = get_sample_artifacts(
            lims=self.lims, process=self.process
        )
        for sample_artifact in sample_artifacts:
            lane: Optional[int] = get_artifact_lane(sample_artifact)
            sample_lims_id: Optional[str] = get_artifact_lims_id(sample_artifact)

            if not lane or not sample_lims_id:
                LOG.warning(f"Failed to parse sample artifact: {sample_artifact}")
                continue

            self.sample_artifacts[sample_lims_id] = {lane: sample_artifact}

    @property
    def flow_cell_name(self) -> str:
        flow_cell_name: Optional[str] = get_flow_cell_name(self.process)
        if not flow_cell_name:
            raise LimsError("Q30 threshold not set")
        return flow_cell_name

    @property
    def q30_threshold(self) -> int:
        q30_threshold: Optional[int] = get_q30_threshold(self.process)
        if not q30_threshold:
            raise LimsError("Q30 threshold not set")
        return q30_threshold

    def _get_sample_artifact(
        self, sample_lims_id: str, lane: int
    ) -> Optional[Artifact]:
        return self.sample_artifacts.get(sample_lims_id, {}).get(lane)

    def update_sample(
        self,
        sample_lims_id: str,
        lane: int,
        reads: int,
        q30_score: float,
        passed_quality_control: bool,
    ) -> None:
        sample_artifact: Optional[Artifact] = self._get_sample_artifact(
            sample_lims_id=sample_lims_id, lane=lane
        )

        if not sample_artifact:
            LOG.warning(
                f"No metrics found for {sample_lims_id} in lane {lane}. Skipping."
            )
            return

        set_sample_reads(sample_artifact=sample_artifact, reads=reads)
        set_sample_q30_score(sample_artifact=sample_artifact, q30_score=q30_score)
        set_quality_check_flag(
            artifact=sample_artifact, quality_check_passed=passed_quality_control
        )

        sample_artifact.put()
