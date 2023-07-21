import sys

from cg_lims.status_db_api import StatusDBAPI


class SequencingQualityChecker:
    READS_MIN_THRESHOLD = 1000

    def __init__(self, process, status_db_api: StatusDBAPI):
        self.process = process
        self.sample_artifacts = {}
        self.sequencing_metrics = []

        self.not_updated_artifacts = self.count_single_sample_artifacts()
        self.updated_artifacts_count = 0
        self.failed_artifacts_count = 0

        self.status_db_api = status_db_api

    def get_and_set_sample_artifacts(self):
        """Preparing output artifact dict."""
        for input_output in self.process.input_output_maps:
            input_map = input_output[0]
            output_map = input_output[1]
            if output_map["output-generation-type"] == "PerReagentLabel":
                artifact = output_map["uri"]
                sample_name = artifact.samples[0].id
                lane = input_map["uri"].location[1][0]
                if sample_name not in self.sample_artifacts:
                    self.sample_artifacts[sample_name] = {lane: artifact}
                else:
                    self.sample_artifacts[sample_name][lane] = artifact

    def get_and_set_flow_cell_name(self):
        """
        Raises:
            Exception: If the flow cell name cannot be found.
        """
        try:
            self.flow_cell_name = self.process.all_inputs()[0].container.name
        except Exception as e:
            raise Exception("Could not find flow cell name.") from e

    def get_and_set_sequencing_metrics(self):
        try:
            metrics = self.status_db_api.get_sequencing_metrics_for_flow_cell(
                self.flow_cell_name
            )
            self.sequencing_metrics = metrics

        except Exception as e:
            sys.exit(
                f"Error getting sequencing metrics for flowcell: {self.flow_cell_name}, {e}"
            )

    def get_and_set_q30_threshold(self):
        q30_threshold_setting: str = "Threshold for % bases >= Q30"

        if not q30_threshold_setting in self.process.udf:
            sys.exit(f"{q30_threshold_setting} has not ben set.")

        self.q30_threshold = self.process.udf.get("Threshold for % bases >= Q30")

    def count_single_sample_artifacts(self):
        all_artifacts = self.process.all_outputs(unique=True)
        return len(list(filter(lambda a: len(a.samples) == 1, all_artifacts)))

    def is_valid_quality(self, q30_score: float, reads: int):
        return (
            q30_score * 100 >= self.q30_threshold
            and reads >= SequencingQualityChecker.READS_MIN_THRESHOLD
        )

    def get_quality_control_flag(self, q30, reads):
        if self.is_valid_quality(q30, reads):
            return "PASSED"

        self.failed_artifacts_count += 1
        return "FAILED"

    def quality_control_samples(self):
        for metrics in self.sequencing_metrics:
            sample_lims_id: str = metrics.sample_internal_id

            if sample_lims_id not in self.sample_artifacts:
                continue

            lane = str(metrics.flow_cell_lane_number)
            sample_artifact = self.sample_artifacts[sample_lims_id].get(lane)

            if not sample_artifact:
                continue

            sample_artifact.udf["# Reads"] = metrics.sample_total_reads_in_lane
            sample_artifact.udf["% Bases >=Q30"] = metrics.sample_base_fraction_passing_q30

            qc_flag = self.get_quality_control_flag(
                metrics.sample_base_fraction_passing_q30,
                metrics.sample_total_reads_in_lane,
            )
            sample_artifact.qc_flag = qc_flag

            sample_artifact.put()
            self.updated_artifacts_count += 1
            self.not_updated_artifacts -= 1

    def samples_failed_quality_control(self):
        return self.failed_artifacts_count or self.not_updated_artifacts

    def get_quality_summary(self) -> str:
        quality_summary: str = f"Checked {self.updated_artifacts_count} samples. Skipped {self.not_updated_artifacts} samples."

        if self.failed_artifacts_count:
            quality_summary = (
                f"{quality_summary} {self.failed_artifacts_count} samples failed QC!"
            )

        return quality_summary

    def validate_flow_cell_sequencing_quality(self):
        self.get_and_set_q30_threshold()
        self.get_and_set_flow_cell_name()
        self.get_and_set_sample_artifacts()
        self.get_and_set_sequencing_metrics()
        self.quality_control_samples()
