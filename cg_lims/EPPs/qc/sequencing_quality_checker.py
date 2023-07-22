import sys
from typing import List
from cg_lims.models.api.sequencing_metrics import SequencingMetrics
from cg_lims.status_db_api import StatusDBAPI
from genologics.entities import Process, Artifact


class ArtifactManager:
    def __init__(self, process: Process):
        self.process = process
        self.sample_artifacts = {}
        self.flow_cell_name = ""
        self.q30_threshold = 0

        self.set_sample_artifacts()
        self.set_flow_cell_name()
        self.set_q30_threshold()

    def set_sample_artifacts(self):
        for input_output in self.process.input_output_maps:
            input_map = input_output[0]
            output_map = input_output[1]
            if self.is_output_per_reagent_label(output_map):
                self.store_sample_artifact(input_map, output_map)

    def is_output_per_reagent_label(self, output_map):
        return output_map["output-generation-type"] == "PerReagentLabel"

    def store_sample_artifact(self, input_map, output_map):
        artifact, lane = self.extract_artifact_and_lane(input_map, output_map)
        sample_name = artifact.samples[0].id
        if sample_name not in self.sample_artifacts:
            self.sample_artifacts[sample_name] = {lane: artifact}
        else:
            self.sample_artifacts[sample_name][lane] = artifact

    def extract_artifact_and_lane(self, input_map, output_map):
        artifact = output_map["uri"]
        lane = input_map["uri"].location[1][0]
        return artifact, int(lane)

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

    def set_sample_reads(self, sample_lims_id: str, lane: int, reads: int):
        sample: Artifact = self.get_sample_artifact(sample_id=sample_lims_id, lane=lane)
        sample.udf["# Reads"] = reads

    def set_sample_q30(self, sample_lims_id: str, lane: int, q30: float):
        sample: Artifact = self.get_sample_artifact(sample_id=sample_lims_id, lane=lane)
        sample.udf["% Bases >=Q30"] = q30

    def set_sample_quality_flag(self, sample_lims_id: str, lane: int, passed: bool):
        sample: Artifact = self.get_sample_artifact(sample_id=sample_lims_id, lane=lane)
        sample.qc_flag = "PASSED" if passed else "FAILED"


class SequencingQualityChecker:
    READS_MIN_THRESHOLD = 1000

    def __init__(self, process: Process, status_db_api: StatusDBAPI) -> None:
        self.artifact_manager = ArtifactManager(process)
        self.status_db_api = status_db_api

        self.samples_not_passing_qc_count = 0


    def validate_sequencing_quality(self) -> str:
        flow_cell_name: str = self.artifact_manager.get_flow_cell_name()
        sequencing_metrics: List[
            SequencingMetrics
        ] = self.status_db_api.get_sequencing_metrics_for_flow_cell(flow_cell_name)

        for metrics in sequencing_metrics:
            sample_id: str = metrics.sample_internal_id
            lane: int = metrics.flow_cell_lane_number

            reads: int = metrics.sample_total_reads_in_lane
            q30_score: float = metrics.sample_base_fraction_passing_q30
            q30_threshold: int = self.artifact_manager.get_q30_threshold()
            reads_threshold: int = SequencingQualityChecker.READS_MIN_THRESHOLD

            passed_qc: bool = self.is_valid_sequencing_quality(
                reads=reads,
                q30_score=q30_score,
                reads_threshold=reads_threshold,
                q30_threshold=q30_threshold,
            )

            self.artifact_manager.set_sample_q30(sample_lims_id=sample_id, lane=lane, q30=q30_score)
            self.artifact_manager.set_sample_reads(sample_lims_id=sample_id, lane=lane, reads=reads)
            self.artifact_manager.set_sample_quality_flag(sample_lims_id=sample_id, lane=lane, passed=passed_qc)

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
            quality_summary = (
                f"{quality_summary} {self.samples_not_passing_qc_count} samples failed QC!"
            )
        return quality_summary

    def samples_failed_quality_control(self):
        return bool(self.samples_failed_quality_control)
