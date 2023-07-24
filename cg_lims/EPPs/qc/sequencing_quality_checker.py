import logging
import sys
from typing import Dict, List, Optional

from genologics.entities import Artifact, Process

from cg_lims.models.api.sequencing_metrics import SequencingMetrics
from cg_lims.status_db_api import StatusDBAPI

LOG = logging.getLogger(__name__)

PER_REAGENT_LABEL = "PerReagentLabel"

Q30_THRESHOLD_FIELD = "Threshold for % bases >= Q30"
READS_FIELD = "# Reads"
Q30_FIELD = "% Bases >=Q30"

URI_KEY = "uri"
OUTPUT_TYPE_KEY = "output-generation-type"

QUALITY_CHECK_PASSED = "PASSED"
QUALITY_CHECK_FAILED = "FAILED"


class SequencingArtifactManager:
    def __init__(self, process: Process):
        self.process: Process = process
        self.sample_artifacts: Dict[str, Dict[int, Artifact]] = {}
        self.flow_cell_name: str = ""
        self.q30_threshold: int = 0

        self._set_sample_artifacts()
        self._set_flow_cell_name()
        self._set_q30_threshold()

    def _set_sample_artifacts(self) -> None:
        for input_map, output_map in self.process.input_output_maps:
            self._process_artifact(input_map=input_map, output_map=output_map)

    def _process_artifact(self, input_map: Dict, output_map: Dict) -> None:
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
            raise ValueError(f"Could not extract sample artifact from output map {output_map}: {e}")

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

    def _set_q30_threshold(self) -> None:
        try:
            self.q30_threshold = self.process.udf[Q30_THRESHOLD_FIELD]
        except (AttributeError, KeyError) as e:
            raise Exception(f"Failed to find Q30 threshold: {e}")

    def _get_sample_artifact(self, sample_lims_id: str, lane: int) -> Optional[Artifact]:
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
        sample: Optional[Artifact] = self._get_sample_artifact(sample_lims_id=sample_lims_id, lane=lane)

        if not sample:
            LOG.warning(f"Failed to update sample {sample_lims_id} in lane {lane}")
            return

        sample.udf[READS_FIELD] = reads
        sample.udf[Q30_FIELD] = q30_score
        sample.qc_flag = self._get_quality_flag(passed_quality_control)
        sample.put()


class SequencingQualityChecker:
    READS_MIN_THRESHOLD = 1000

    def __init__(self, process: Process, status_db_api: StatusDBAPI) -> None:
        self.sample_artifact_manager: SequencingArtifactManager = SequencingArtifactManager(process)
        self.status_db_api: StatusDBAPI = status_db_api

        self.q30_threshold: int = self.sample_artifact_manager.get_q30_threshold()
        self.flow_cell_name: str = self.sample_artifact_manager.get_flow_cell_name()
        self.samples_not_passing_qc_count: int = 0

    def validate_sequencing_quality(self) -> str:
        LOG.info(f"Validating sequencing quality for flow cell {self.flow_cell_name}") 

        sequencing_metrics: List[SequencingMetrics] = self.status_db_api.get_sequencing_metrics_for_flow_cell(self.flow_cell_name)

        for metrics in sequencing_metrics:
            self._validate_sequencing_metrics(metrics)

        return self._get_quality_summary()

    def _validate_sequencing_metrics(self, metrics: SequencingMetrics) -> None:
        sample_lims_id: str = metrics.sample_internal_id
        lane: int = metrics.flow_cell_lane_number
        reads: int = metrics.sample_total_reads_in_lane
        q30_score: float = metrics.sample_base_fraction_passing_q30

        passed_quality_control: bool = self._is_valid_sequencing_quality(
            reads=reads,
            q30_score=q30_score,
        )

        self.sample_artifact_manager.update_sample(
            sample_lims_id=sample_lims_id,
            lane=lane,
            reads=reads,
            q30_score=q30_score,
            passed_quality_control=passed_quality_control,
        )

        if not passed_quality_control:
            LOG.warning(f"Sample {sample_lims_id} failed QC check in lane {lane}")
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
