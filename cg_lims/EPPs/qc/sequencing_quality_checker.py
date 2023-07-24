import sys
from typing import Dict, List
from cg_lims.models.api.sequencing_metrics import SequencingMetrics
from cg_lims.status_db_api import StatusDBAPI
from genologics.entities import Process, Artifact


PER_REAGENT_LABEL = "PerReagentLabel"
URI_KEY = "uri"
OUTPUT_TYPE_KEY = "output-generation-type"


class SequencingArtifactManager:
    def __init__(self, process: Process):
        self.process = process
        self.sample_artifacts = {}
        self.flow_cell_name = ""
        self.q30_threshold = 0

        self.extract_and_store_sample_artifacts()
        self.set_flow_cell_name()
        self.set_q30_threshold()

    def extract_and_store_sample_artifacts(self) -> None:
        for input_map, output_map in self.process.input_output_maps:
            if self.is_output_per_reagent_label(output_map):
                self.store_sample_artifact(input_map=input_map, output_map=output_map)

    def is_output_per_reagent_label(self, output_map: Dict) -> bool:
        return output_map.get(OUTPUT_TYPE_KEY) == PER_REAGENT_LABEL

    def store_sample_artifact(self, input_map: Dict, output_map: Dict) -> None:
        try:
            sample: Artifact = self.extract_sample_artifact_from_output_map(output_map)
            lane: int = self.extract_lane_from_input_map(input_map)
            self.add_sample_artifact_to_dict(sample, lane)
        except ValueError as e:
            # Log error
            return

    def extract_lane_from_input_map(self, input_map: Dict) -> int:
        try:
            lane: str = input_map["uri"].location[1][0]
            return int(lane)
        except (KeyError, IndexError, ValueError, AttributeError) as e:
            raise ValueError(f"Could not extract lane: {e}")

    def extract_sample_artifact_from_output_map(self, output_map: Dict) -> Artifact:
        try:
            return output_map["uri"]
        except KeyError as e:
            raise ValueError(f"Could not extract sample artifact: {e}")

    def add_sample_artifact_to_dict(self, sample_artifact: Artifact, lane: int) -> None:
        sample_name: str = sample_artifact.samples[0].id
        if sample_name not in self.sample_artifacts:
            self.sample_artifacts[sample_name] = {lane: sample_artifact}
        else:
            self.sample_artifacts[sample_name][lane] = sample_artifact

    def set_flow_cell_name(self):
        container_artifact = self.process.all_inputs()[0].container

        if not container_artifact or not container_artifact.name:
            sys.exit("Flow cell name not found")

        self.flow_cell_name = container_artifact.name

    def get_sample_artifact(self, sample_id: str, lane: int) -> Artifact:
        try:
            return self.sample_artifacts[sample_id][lane]
        except KeyError:
            raise ValueError(f"No artifact found for sample {sample_id} in lane {lane}")

    def get_flow_cell_name(self):
        return self.flow_cell_name

    def get_q30_threshold(self):
        return self.q30_threshold

    def set_q30_threshold(self):
        q30_threshold_setting: str = "Threshold for % bases >= Q30"
        if not q30_threshold_setting in self.process.udf:
            sys.exit(f"{q30_threshold_setting} has not ben set.")
        self.q30_threshold = self.process.udf.get(q30_threshold_setting)

    def update_sample_artifact(
        self, sample_id: str, lane: int, reads: int, q30: float, passed_qc: bool
    ) -> None:
        """Update the UDFs of a sample artifact."""
        sample: Artifact = self.get_sample_artifact(sample_id, lane)
        sample.udf["# Reads"] = reads
        sample.udf["% Bases >=Q30"] = q30
        sample.qc_flag = "PASSED" if passed_qc else "FAILED"


class SequencingQualityChecker:
    READS_MIN_THRESHOLD = 1000

    def __init__(self, process: Process, status_db_api: StatusDBAPI) -> None:
        self.sample_artifact_manager = SequencingArtifactManager(process)
        self.status_db_api = status_db_api

        self.samples_not_passing_qc_count = 0

    def validate_sequencing_quality(self) -> str:
        flow_cell_name: str = self.sample_artifact_manager.get_flow_cell_name()
        sequencing_metrics: List[
            SequencingMetrics
        ] = self.status_db_api.get_sequencing_metrics_for_flow_cell(flow_cell_name)

        for metrics in sequencing_metrics:
            reads: int = metrics.sample_total_reads_in_lane
            q30_score: float = metrics.sample_base_fraction_passing_q30

            q30_threshold: int = self.sample_artifact_manager.get_q30_threshold()
            reads_threshold: int = SequencingQualityChecker.READS_MIN_THRESHOLD

            passed_qc: bool = self.is_valid_sequencing_quality(
                reads=reads,
                q30_score=q30_score,
                reads_threshold=reads_threshold,
                q30_threshold=q30_threshold,
            )

            self.sample_artifact_manager.update_sample_artifact(
                sample_id=metrics.sample_internal_id,
                lane=metrics.flow_cell_lane_number,
                reads=metrics.sample_total_reads_in_lane,
                q30=q30_score,
                passed_qc=passed_qc,
            )

            if not passed_qc:
                self.samples_not_passing_qc_count += 1

        return self.get_quality_summary()

    def is_valid_sequencing_quality(
        self, q30_score: float, q30_threshold: int, reads: int, reads_threshold: int
    ):
        passes_q30_threshold: bool = q30_score * 100 >= q30_threshold
        passes_read_threshold: bool = reads >= reads_threshold
        return passes_q30_threshold and passes_read_threshold

    def get_quality_summary(self) -> str:
        quality_summary: str = f"Validated samples."

        if self.samples_not_passing_qc_count:
            quality_summary = f"{quality_summary} {self.samples_not_passing_qc_count} samples failed QC!"
        return quality_summary

    def samples_failed_quality_control(self):
        return self.samples_not_passing_qc_count > 0
