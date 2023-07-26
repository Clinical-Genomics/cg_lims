import logging
import sys
from typing import Dict, List, Optional

from genologics.entities import Artifact, Process
from cg_lims.EPPs.files.sample_sheet.create_sample_sheet import get_artifact_lane


from cg_lims.get.artifacts import get_output_artifacts
from genologics.lims import Lims

from cg_lims.get.fields import get_artifact_lims_id

LOG = logging.getLogger(__name__)


PER_REAGENT_LABEL = "PerReagentLabel"
Q30_THRESHOLD_FIELD = "Threshold for % bases >= Q30"
READS_FIELD = "# Reads"
Q30_FIELD = "% Bases >=Q30"
QUALITY_CHECK_PASSED = "PASSED"
QUALITY_CHECK_FAILED = "FAILED"


class SequencingArtifactManager:
    def __init__(self, process: Process, lims: Lims):
        self.process: Process = process
        self.lims: Lims = lims

        self.sample_artifacts: Dict[str, Dict[int, Artifact]] = {}
        self.flow_cell_name: str = ""
        self.q30_threshold: int = 0

        self._set_sample_artifacts()
        self._set_flow_cell_name()
        self._set_q30_threshold()

    def _set_sample_artifacts(self) -> None:
        sample_artifacts: List[Artifact] = get_output_artifacts(
            lims=self.lims,
            process=self.process,
            output_type="Analyte",
            output_generation_type=[PER_REAGENT_LABEL],
        )
        for sample_artifact in sample_artifacts:
            try:
                lane: int = get_artifact_lane(sample_artifact)
                sample_lims_id: str = get_artifact_lims_id(sample_artifact)
                self.sample_artifacts[sample_lims_id] = {lane: sample_artifact}
            except ValueError as error:
                LOG.warning(f"Failed to parse sample artifact: {error}")

    def _set_flow_cell_name(self) -> None:
        try:
            container = self.process.all_inputs()[0].container
            if container is None:
                raise ValueError("Container is None")
            flow_cell_name = container.name
            if flow_cell_name is None:
                raise ValueError("Flow cell name is None")
            self.flow_cell_name = flow_cell_name
        except (AttributeError, IndexError, TypeError, ValueError) as e:
            sys.exit(f"Failed to find flow cell name: {e}")

    def _set_q30_threshold(self) -> None:
        try:
            self.q30_threshold = self.process.udf[Q30_THRESHOLD_FIELD]
        except (AttributeError, KeyError) as e:
            raise Exception(f"Failed to find Q30 threshold: {e}")

    def _get_sample_artifact(
        self, sample_lims_id: str, lane: int
    ) -> Optional[Artifact]:
        return self.sample_artifacts.get(sample_lims_id, {}).get(lane)

    def _get_quality_flag(self, passed_qc: bool) -> str:
        return QUALITY_CHECK_PASSED if passed_qc else QUALITY_CHECK_FAILED

    def get_flow_cell_name(self) -> str:
        return self.flow_cell_name

    def get_q30_threshold(self) -> int:
        return self.q30_threshold

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
            LOG.warning(f"Failed to update sample {sample_lims_id} in lane {lane}")
            return

        sample_artifact.udf[READS_FIELD] = reads
        sample_artifact.udf[Q30_FIELD] = q30_score
        sample_artifact.qc_flag = self._get_quality_flag(passed_quality_control)
        sample_artifact.put()
