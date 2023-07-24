import logging
import sys
from typing import Dict, List

from genologics.entities import Artifact, Process

from cg_lims.models.api.sequencing_metrics import SequencingMetrics
from cg_lims.status_db_api import StatusDBAPI

LOG = logging.getLogger(__name__)

PER_REAGENT_LABEL = "PerReagentLabel"
Q30_THRESHOLD_SETTING = "Threshold for % bases >= Q30"
URI_KEY = "uri"
OUTPUT_TYPE_KEY = "output-generation-type"


class SequencingArtifactManager:
    def __init__(self, process: Process):
        self.process = process
        self.sample_artifacts = {}
        self.flow_cell_name = ""
        self.q30_threshold = 0

        self._set_sample_artifacts()
        self._set_flow_cell_name()
        self._set_q30_threshold()

    def _set_sample_artifacts(self) -> None:
        for input_map, output_map in self.process.input_output_maps:
            if self._is_output_per_reagent_label(output_map):
                try:
                    sample: Artifact = self._extract_sample_artifact(output_map)
                    lane: int = self._extract_lane(input_map)
                    self._store_sample_artifact(sample=sample, lane=lane)
                except ValueError as error:
                    LOG.warning(f"Failed to parse sample artifact: {error}")

    def _is_output_per_reagent_label(self, output_map: Dict) -> bool:
        return output_map.get(OUTPUT_TYPE_KEY) == PER_REAGENT_LABEL

    def _extract_lane(self, input_map: Dict) -> int:
        try:
            lane: str = input_map["uri"].location[1][0]
            return int(lane)
        except (AttributeError, IndexError, KeyError, ValueError) as e:
            raise ValueError(f"Could not extract lane from input map {input_map}: {e}")

    def _extract_sample_artifact(self, output_map: Dict) -> Artifact:
        try:
            return output_map["uri"]
        except KeyError as e:
            raise ValueError(
                f"Could not extract sample artifact from output map {output_map}: {e}"
            )

    def _extract_sample_lims_id(self, sample: Artifact) -> str:
        try:
            sample_lims_id = sample.samples[0].id
            if sample_lims_id is None:
                raise ValueError("Sample id is None")
            return sample_lims_id
        except (AttributeError, IndexError) as e:
            raise ValueError(f"Could not extract sample id: {e}")

    def _store_sample_artifact(self, sample: Artifact, lane: int) -> None:
        sample_lims_id: str = self._extract_sample_lims_id(sample)
        if sample_lims_id not in self.sample_artifacts:
            self.sample_artifacts[sample_lims_id] = {lane: sample}
        else:
            self.sample_artifacts[sample_lims_id][lane] = sample

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

    def _set_q30_threshold(self):
        try:
            self.q30_threshold = self.process.udf[Q30_THRESHOLD_SETTING]
        except (AttributeError, KeyError) as e:
            sys.exit(f"Failed to find q30 threshold: {e}")

    def _get_sample_artifact(self, sample_lims_id: str, lane: int) -> Artifact:
        try:
            return self.sample_artifacts[sample_lims_id][lane]
        except KeyError:
            raise ValueError(
                f"No artifact found for sample {sample_lims_id} in lane {lane}"
            )

    def get_flow_cell_name(self) -> str:
        return self.flow_cell_name

    def get_q30_threshold(self):
        return self.q30_threshold

    def update_sample_artifact(
        self,
        sample_lims_id: str,
        lane: int,
        reads: int,
        q30_score: float,
        passed_qc: bool,
    ) -> None:
        try:
            sample_artifact: Artifact = self._get_sample_artifact(
                sample_lims_id=sample_lims_id, lane=lane
            )
            sample_artifact.udf["# Reads"] = reads
            sample_artifact.udf["% Bases >=Q30"] = q30_score
            sample_artifact.qc_flag = "PASSED" if passed_qc else "FAILED"
        except ValueError as error:
            LOG.warning(
                f"Failed to update sample {sample_lims_id} in lane {lane}: {error}"
            )


class SequencingQualityChecker:
    READS_MIN_THRESHOLD = 1000

    def __init__(self, process: Process, status_db_api: StatusDBAPI) -> None:
        self.sample_artifact_manager = SequencingArtifactManager(process)
        self.status_db_api = status_db_api

        self.q30_threshold = self.sample_artifact_manager.get_q30_threshold()
        self.flow_cell_name = self.sample_artifact_manager.get_flow_cell_name()
        self.samples_not_passing_qc_count = 0

    def validate_sequencing_quality(self) -> str:
        flow_cell_name: str = self.sample_artifact_manager.get_flow_cell_name()
        sequencing_metrics: List[
            SequencingMetrics
        ] = self.status_db_api.get_sequencing_metrics_for_flow_cell(flow_cell_name)

        for metrics in sequencing_metrics:
            reads: int = metrics.sample_total_reads_in_lane
            q30_score: float = metrics.sample_base_fraction_passing_q30

            passed_qc: bool = self._is_valid_sequencing_quality(
                reads=reads,
                q30_score=q30_score,
            )

            self.sample_artifact_manager.update_sample_artifact(
                sample_lims_id=metrics.sample_internal_id,
                lane=metrics.flow_cell_lane_number,
                reads=metrics.sample_total_reads_in_lane,
                q30_score=q30_score,
                passed_qc=passed_qc,
            )

            if not passed_qc:
                self.samples_not_passing_qc_count += 1

        return self._get_quality_summary()

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
