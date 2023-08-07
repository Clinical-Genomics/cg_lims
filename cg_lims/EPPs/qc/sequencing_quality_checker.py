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
        self.sample_lanes_in_metrics = set()

    def _track_sample_lane(self, metrics: SampleLaneSequencingMetrics) -> None:
        sample_lane = (metrics.sample_internal_id, metrics.flow_cell_lane_number)
        self.sample_lanes_in_metrics.add(sample_lane)

    def _get_sequencing_metrics(self) -> List[SampleLaneSequencingMetrics]:
        try:
            return self.status_db_api.get_sequencing_metrics_for_flow_cell(
                self.flow_cell_name
            )
        except LimsError as e:
            error_message: str = f"Could not retrieve sequencing metrics for {self.flow_cell_name}: {e}"
            LOG.error(error_message)
            sys.exit(error_message)

    def validate_sequencing_quality(self) -> str:
        LOG.info(f"Validating sequencing quality for flow cell {self.flow_cell_name}")

        sequencing_metrics = self._get_sequencing_metrics()

        for metrics in sequencing_metrics:
            passed_qc: bool = self._validate_sequencing_metrics(metrics)
            self._update_sample_with_quality_results(metrics, passed_qc)
            self._log_and_count_failed_samples(metrics, passed_qc)
            self._track_sample_lane(metrics)

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

    def _log_and_count_failed_samples(
        self, metrics: SampleLaneSequencingMetrics, passed_quality_control: bool
    ) -> None:
        """Log the failed samples and increment the count."""
        if not passed_quality_control:
            LOG.warning(f"Sample {metrics.sample_internal_id} failed QC check in lane {metrics.flow_cell_lane_number}")
            self.samples_not_passing_qc_count += 1

    def _validate_sequencing_metrics(
        self, metrics: SampleLaneSequencingMetrics
    ) -> None:
        return self._passes_thresholds(
            reads=metrics.sample_total_reads_in_lane,
            q30_score=metrics.sample_base_fraction_passing_q30,
        )

    def _passes_thresholds(self, q30_score: float, reads: int) -> bool:
        passes_q30_threshold: bool = q30_score * 100 >= self.q30_threshold
        passes_read_threshold: bool = reads >= self.READS_MIN_THRESHOLD
        return passes_q30_threshold and passes_read_threshold

    def _get_samples_only_in_lims(self) -> List[str]:
        sample_lanes_in_lims = self.artifact_manager.sample_lanes_in_lims()
        return list(sample_lanes_in_lims - self.sample_lanes_in_metrics)

    def _get_samples_only_in_metrics(self):
        sample_lanes_in_lims = self.artifact_manager.sample_lanes_in_lims()
        return list(self.sample_lanes_in_metrics - sample_lanes_in_lims)

    def _generate_summary(self) -> str:
        quality_summary: str = f"Validated samples."

        samples_only_in_metrics = self._get_samples_only_in_metrics()
        samples_only_in_lims = self._get_samples_only_in_lims()

        if self.samples_not_passing_qc_count:
            quality_summary = f"{quality_summary} {self.samples_not_passing_qc_count} samples failed QC!"

        if samples_only_in_metrics:
            quality_summary = f"{quality_summary} Could not find in lims: {samples_only_in_metrics}."

        if samples_only_in_lims:
            quality_summary = f"{quality_summary} Could not find metrics for: {samples_only_in_lims}."

        return quality_summary

    def samples_failed_quality_control(self):
        return self.samples_not_passing_qc_count > 0
