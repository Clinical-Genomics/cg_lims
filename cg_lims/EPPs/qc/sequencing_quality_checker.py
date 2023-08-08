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
        self, cg_api_client: StatusDBAPI, artifact_manager: SequencingArtifactManager
    ) -> None:
        self.artifact_manager: SequencingArtifactManager = artifact_manager
        self.cg_api_client: StatusDBAPI = cg_api_client

        self.q30_threshold = self.artifact_manager.q30_threshold
        self.flow_cell_name = self.artifact_manager.flow_cell_name

        self.sample_lanes_in_metrics = set()
        self.failed_sample_count = 0


    def _track_sample_lane(self, metrics: SampleLaneSequencingMetrics) -> None:
        sample_lane = (metrics.sample_internal_id, metrics.flow_cell_lane_number)
        self.sample_lanes_in_metrics.add(sample_lane)

    def _get_sequencing_metrics(self) -> List[SampleLaneSequencingMetrics]:
        return self.cg_api_client.get_sequencing_metrics_for_flow_cell(self.flow_cell_name)

    def validate_sequencing_quality(self) -> str:
        """Validate the sequencing data for each sample on a flow cell based on the number of reads and q30 scores."""
        LOG.info(f"Validating sequencing quality for flow cell {self.flow_cell_name}")

        sequencing_metrics = self._get_sequencing_metrics()

        for metrics in sequencing_metrics:
            self._track_sample_lane(metrics)
            passed_qc = self._quality_control(metrics)
            self._update_sample_with_quality_results(metrics=metrics, passed_quality_control=passed_qc)

            if not passed_qc:
                self.failed_sample_count += 1

        return self._generate_summary()

    def _update_sample_with_quality_results(
        self, metrics: SampleLaneSequencingMetrics, passed_quality_control: bool
    ) -> None:
        self.artifact_manager.update_sample(
            sample_id=metrics.sample_internal_id,
            lane=metrics.flow_cell_lane_number,
            reads=metrics.sample_total_reads_in_lane,
            q30_score=metrics.sample_base_fraction_passing_q30,
            passed_quality_control=passed_quality_control,
        )

    def _quality_control(
        self, metrics: SampleLaneSequencingMetrics
    ) -> None:
        return self._passes_thresholds(
            reads=metrics.sample_total_reads_in_lane,
            q30_score=metrics.sample_base_fraction_passing_q30,
        )

    def _passes_thresholds(self, q30_score: float, reads: int) -> bool:
        passes_q30_threshold = q30_score * 100 >= self.q30_threshold
        passes_read_threshold = reads >= self.READS_MIN_THRESHOLD
        return passes_q30_threshold and passes_read_threshold

    def _get_samples_only_in_lims(self) -> List[str]:
        sample_lanes_in_lims = self.artifact_manager.sample_lanes_in_lims()
        return list(sample_lanes_in_lims - self.sample_lanes_in_metrics)

    def _get_samples_only_in_metrics(self):
        sample_lanes_in_lims = self.artifact_manager.sample_lanes_in_lims()
        return list(self.sample_lanes_in_metrics - sample_lanes_in_lims)

    def _generate_summary(self) -> str:
        messages = ["Validated samples."]

        samples_only_in_metrics = self._get_samples_only_in_metrics()
        samples_only_in_lims = self._get_samples_only_in_lims()

        if self.failed_sample_count:
            messages.append(f"{self.failed_sample_count} samples failed the quality control!")
        
        if samples_only_in_metrics:
            messages.append(f"Could not find in lims: {samples_only_in_metrics}.")
        
        if samples_only_in_lims:
            messages.append(f"Could not find metrics for: {samples_only_in_lims}.")

        return " ".join(messages)

    def samples_failed_quality_control(self):
        return self.failed_sample_count > 0
