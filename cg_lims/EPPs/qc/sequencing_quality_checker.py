import logging
from typing import List

from cg_lims.clients.cg.models import SampleLaneSequencingMetrics
from cg_lims.clients.cg.status_db_api import StatusDBAPI
from cg_lims.EPPs.qc.models import SampleLane, SampleLaneSet
from cg_lims.EPPs.qc.sequencing_artifact_manager import SequencingArtifactManager
from cg_lims.exceptions import MissingSampleError
from cg_lims.get.samples import is_negative_control
from genologics.entities import Sample
from genologics.lims import Lims

LOG = logging.getLogger(__name__)


MISSING_IN_LIMS_MSG = (
    "Found sequencing metrics for the following sample lane combinations, "
    "but they are not present in LIMS:"
)

MISSING_IN_METRICS_MSG = "No metrics were found for the following sample lane artifacts:"


class SequencingQualityChecker:
    """This class contains the logic for validating the sequencing quality of a flow cell."""

    READS_MIN_THRESHOLD = 1000

    def __init__(
        self, cg_api_client: StatusDBAPI, artifact_manager: SequencingArtifactManager
    ) -> None:
        self.artifact_manager: SequencingArtifactManager = artifact_manager
        self.cg_api_client: StatusDBAPI = cg_api_client

        self.q30_threshold: int = self.artifact_manager.q30_threshold
        self.flow_cell_name: str = self.artifact_manager.flow_cell_name

        self.metrics: List[SampleLaneSequencingMetrics] = []
        self.failed_qc_count: int = 0

    def _get_sequencing_metrics(self) -> List[SampleLaneSequencingMetrics]:
        metrics = self.cg_api_client.get_sequencing_metrics_for_flow_cell(self.flow_cell_name)
        self.metrics = metrics
        return metrics

    def validate_sequencing_quality(self, lims: Lims) -> str:
        """Validate the sequencing data for each sample in all lanes on a flow cell based on the number of reads and q30 scores."""
        LOG.info(f"Validating sequencing quality for flow cell {self.flow_cell_name}")

        sequencing_metrics = self._get_sequencing_metrics()

        for metrics in sequencing_metrics:
            passed_qc: bool = self._quality_control(metrics=metrics, lims=lims)
            self._update_sample_with_quality_results(
                metrics=metrics, passed_quality_control=passed_qc
            )

            if not passed_qc:
                self.failed_qc_count += 1

        self.failed_qc_count += len(self._get_sample_lanes_not_in_metrics())

        return self._generate_summary()

    def _update_sample_with_quality_results(
        self, metrics: SampleLaneSequencingMetrics, passed_quality_control: bool
    ) -> None:
        self.artifact_manager.update_sample(
            sample_id=metrics.sample_internal_id,
            lane=metrics.flow_cell_lane_number,
            reads=metrics.sample_total_reads_in_lane,
            q30_score=metrics.sample_base_percentage_passing_q30,
            passed_quality_control=passed_quality_control,
        )

    def _quality_control(self, metrics: SampleLaneSequencingMetrics, lims: Lims) -> bool:
        try:
            sample: Sample = Sample(lims=lims, id=metrics.sample_internal_id)
            negative_control: bool = is_negative_control(sample=sample)
            return self._passes_quality_thresholds(
                reads=metrics.sample_total_reads_in_lane,
                q30_score=metrics.sample_base_percentage_passing_q30,
                negative_control=negative_control,
            )
        except MissingSampleError:
            return self._passes_quality_thresholds(
                reads=metrics.sample_total_reads_in_lane,
                q30_score=metrics.sample_base_percentage_passing_q30,
                negative_control=False,
            )

    def _passes_quality_thresholds(
        self, q30_score: float, reads: int, negative_control: bool
    ) -> bool:
        """Check if the provided metrics pass the minimum quality thresholds. Negative controls always pass."""
        if negative_control:
            return True
        passes_q30_threshold = q30_score >= self.q30_threshold
        passes_read_threshold = reads >= self.READS_MIN_THRESHOLD
        return passes_q30_threshold and passes_read_threshold

    def _get_sample_lanes_in_metrics(self) -> SampleLaneSet:
        sample_lanes = set()
        for metrics in self.metrics:
            sample_lane = (metrics.sample_internal_id, metrics.flow_cell_lane_number)
            sample_lanes.add(sample_lane)
        return sample_lanes

    def _get_sample_lanes_not_in_metrics(self) -> List[SampleLane]:
        in_lims: SampleLaneSet = self.artifact_manager.get_sample_lanes_in_lims()
        in_metrics: SampleLaneSet = self._get_sample_lanes_in_metrics()
        return list(in_lims - in_metrics)

    def _get_sample_lanes_only_in_metrics(self) -> List[SampleLane]:
        in_lims: SampleLaneSet = self.artifact_manager.get_sample_lanes_in_lims()
        in_metrics: SampleLaneSet = self._get_sample_lanes_in_metrics()
        return list(in_metrics - in_lims)

    def _generate_summary(self) -> str:
        sample_lane_count: int = len(self.artifact_manager.get_sample_lanes_in_lims())
        messages = [
            f"Validated sequencing quality for flow cell {self.flow_cell_name} with {sample_lane_count} artifacts.\n"
        ]

        only_in_metrics = self._get_sample_lanes_only_in_metrics()
        missing_in_metrics = self._get_sample_lanes_not_in_metrics()

        if self.failed_qc_count:
            messages.append(f"{self.failed_qc_count} artifacts failed the quality control!\n")

        if only_in_metrics:
            messages.append(f"{MISSING_IN_LIMS_MSG} {only_in_metrics}.\n")

        if missing_in_metrics:
            messages.append(f"{MISSING_IN_METRICS_MSG} {missing_in_metrics}.")

        if not self.failed_qc_count and not missing_in_metrics:
            messages.append("All sample lane artifacts in LIMS passed the quality control!")

        return "".join(messages)

    def get_brief_summary(self) -> str:
        """Return a brief summary of the validation results."""
        messages = []

        if self.failed_qc_count:
            messages.append(
                f"{self.failed_qc_count} sample lane artifacts failed the quality control!"
            )
        else:
            messages.append("All sample lane artifacts in LIMS passed the quality control!")

        sample_lane_count: int = len(self.artifact_manager.get_sample_lanes_in_lims())
        messages.append(
            f"Validated sequencing quality for flow cell {self.flow_cell_name} with {sample_lane_count} artifacts."
        )

        return " ".join(messages)

    def samples_failed_quality_control(self) -> bool:
        return self.failed_qc_count > 0
