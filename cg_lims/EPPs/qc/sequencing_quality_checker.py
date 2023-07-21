import sys
from cg_lims.models.api.sequencing_metrics import SequencingMetrics
from cg_lims.status_db_api import StatusDBAPI


class SequencingQualityChecker:
    READS_MIN_THRESHOLD = 1000

    def __init__(self, process, status_db_api: StatusDBAPI):
        self.process = process
        self.sample_artifacts = {}
        self.sequencing_metrics = []
        self.status_db_api = status_db_api
        self.failed_artifacts_count = 0
        self.not_updated_artifacts = self.count_single_sample_artifacts()
        self.updated_artifacts_count = 0

    def validate_flow_cell_sequencing_quality(self):
        self.set_artifacts_and_metrics()
        self.update_sample_artifacts_with_metrics()

    def count_single_sample_artifacts(self):
        all_artifacts = self.process.all_outputs(unique=True)
        return len(list(filter(lambda a: len(a.samples) == 1, all_artifacts)))

    def set_artifacts_and_metrics(self):
        self.set_sample_artifacts()
        self.set_flow_cell_name()
        self.set_sequencing_metrics()
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
        artifact, lane = self.get_artifact_and_lane(input_map, output_map)
        sample_name = artifact.samples[0].id
        if sample_name not in self.sample_artifacts:
            self.sample_artifacts[sample_name] = {lane: artifact}
        else:
            self.sample_artifacts[sample_name][lane] = artifact

    def get_artifact_and_lane(self, input_map, output_map):
        artifact = output_map["uri"]
        lane = input_map["uri"].location[1][0]
        return artifact, lane

    def set_flow_cell_name(self):
        try:
            self.flow_cell_name = self.process.all_inputs()[0].container.name
        except Exception as e:
            raise Exception("Could not find flow cell name.") from e

    def set_sequencing_metrics(self):
        try:
            self.sequencing_metrics = (
                self.status_db_api.get_sequencing_metrics_for_flow_cell(
                    self.flow_cell_name
                )
            )
        except Exception as e:
            sys.exit(
                f"Error getting sequencing metrics for flowcell: {self.flow_cell_name}, {e}"
            )

    def set_q30_threshold(self):
        q30_threshold_setting: str = "Threshold for % bases >= Q30"
        if not q30_threshold_setting in self.process.udf:
            sys.exit(f"{q30_threshold_setting} has not ben set.")
        self.q30_threshold = self.process.udf.get(q30_threshold_setting)

    def update_sample_artifacts_with_metrics(self):
        for metrics in self.sequencing_metrics:
            sample_artifact = self.get_sample_artifact(metrics)
            if sample_artifact:
                self.update_sample_artifact(sample_artifact, metrics)
                self.updated_artifacts_count += 1
                self.not_updated_artifacts -= 1

    def get_sample_artifact(self, metrics: SequencingMetrics):
        sample_lims_id: str = metrics.sample_internal_id
        lane = str(metrics.flow_cell_lane_number)
        return self.sample_artifacts.get(sample_lims_id, {}).get(lane)

    def update_sample_artifact(self, sample_artifact, metrics: SequencingMetrics):
        sample_artifact.udf["# Reads"] = metrics.sample_total_reads_in_lane
        sample_artifact.udf["% Bases >=Q30"] = metrics.sample_base_fraction_passing_q30
        sample_artifact.qc_flag = self.get_quality_control_flag(metrics)
        sample_artifact.put()

    def get_quality_control_flag(self, metrics):
        if self.is_valid_quality(metrics):
            return "PASSED"
        self.failed_artifacts_count += 1
        return "FAILED"

    def is_valid_quality(self, metrics):
        return (
            metrics.sample_base_fraction_passing_q30 * 100 >= self.q30_threshold
            and metrics.sample_total_reads_in_lane
            >= SequencingQualityChecker.READS_MIN_THRESHOLD
        )

    def get_quality_summary(self) -> str:
        quality_summary: str = f"Checked {self.updated_artifacts_count} samples. Skipped {self.not_updated_artifacts} samples."
        if self.failed_artifacts_count:
            quality_summary = (
                f"{quality_summary} {self.failed_artifacts_count} samples failed QC!"
            )
        return quality_summary

    def samples_failed_quality_control(self):
        return self.failed_artifacts_count or self.not_updated_artifacts
