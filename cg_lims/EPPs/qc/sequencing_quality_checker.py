import logging
import sys
from typing import List

from cg_lims.EPPs.qc.sequencing_artifact_manager import SequencingArtifactManager
from cg_lims.exceptions import LimsError
from cg_lims.models.sequencing_metrics import SampleLaneSequencingMetrics
from cg_lims.status_db_api import StatusDBAPI

LOG = logging.getLogger(__name__)


class SequencingQualityChecker:
    READS_MIN_THRESHOLD = 1000

    def __init__(
        self, status_db_api: StatusDBAPI, artifact_manager: SequencingArtifactManager
    ) -> None:
        self.artifact_manager: SequencingArtifactManager = artifact_manager
        self.status_db_api: StatusDBAPI = status_db_api

        self.q30_threshold: int = self.artifact_manager.q30_threshold
        self.flow_cell_name: str = self.artifact_manager.flow_cell_name

        self.samples_not_passing_qc_count: int = 0

    def validate_sequencing_quality(self) -> str:
        LOG.info(f"Validating sequencing quality for flow cell {self.flow_cell_name}") 

        try:
            sequencing_metrics: List[SampleLaneSequencingMetrics] = self.status_db_api.get_sequencing_metrics_for_flow_cell(self.flow_cell_name)
        except LimsError as e:
            error_message: str = f"Could not retrieve sequencing metrics for {self.flow_cell_name}: {e}"
            LOG.error(error_message)
            sys.exit(error_message)

        for metrics in sequencing_metrics:
            self._validate_sequencing_metrics(metrics)

        return self._get_quality_summary()

    def _validate_sequencing_metrics(self, metrics: SampleLaneSequencingMetrics) -> None:
        passed_quality_control: bool = self._is_valid_sequencing_quality(
            reads=metrics.sample_total_reads_in_lane,
            q30_score=metrics.sample_base_fraction_passing_q30,
        )

        self.artifact_manager.update_sample(
            sample_id=metrics.sample_internal_id,
            lane=metrics.flow_cell_lane_number,
            reads=metrics.sample_total_reads_in_lane,
            q30_score=metrics.sample_base_fraction_passing_q30,
            passed_quality_control=passed_quality_control,
        )

        if not passed_quality_control:
            LOG.warning(f"Sample {metrics.sample_internal_id} failed QC check in lane {metrics.flow_cell_lane_number}")
            self.samples_not_passing_qc_count += 1


    def _is_valid_sequencing_quality(self, q30_score: float, reads: int):
        passes_q30_threshold: bool = q30_score * 100 >= self.q30_threshold
        passes_read_threshold: bool = reads >= self.READS_MIN_THRESHOLD
        return passes_q30_threshold and passes_read_threshold

    def _get_quality_summary(self) -> str:
        quality_summary: str = f"Validated samples."

        if self.samples_not_passing_qc_count:
            quality_summary = f"{quality_summary} {self.samples_not_passing_qc_count} samples failed QC!"
        return quality_summary

    def samples_failed_quality_control(self):
        return self.samples_not_passing_qc_count > 0
