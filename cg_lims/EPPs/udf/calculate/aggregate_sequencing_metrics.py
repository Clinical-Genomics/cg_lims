import logging
import sys
from typing import List, Optional

import click
from cg_lims import options
from cg_lims.exceptions import ArgumentError, LimsError
from cg_lims.get.artifacts import get_artifacts
from genologics.entities import Artifact, Process, Sample
from genologics.lims import Lims

LOG = logging.getLogger(__name__)


class MetricUdf:
    sample_metric_udf: str
    aggregate_udf: str
    unit_conversion: float

    def __init__(self, sample_metric_udf: str, aggregate_udf: str, unit_conversion: float):
        self.sample_metric_udf = sample_metric_udf
        self.aggregate_udf = aggregate_udf
        self.unit_conversion = unit_conversion


def create_metric_list(
    metric_udfs: List[str], aggregate_metric_udfs: List[str], unit_conversion_factor: List[str]
) -> List[MetricUdf]:
    """
    Return a list of MetricUdf objects given lists of:
        - metrics UDFs (metric_udfs)
        - corresponding aggregate metric UDFs (aggregate_metric_udfs)
        - unit conversion factors (unit_conversion_factor)
    """
    if len(metric_udfs) != len(aggregate_metric_udfs) != len(unit_conversion_factor):
        raise ArgumentError(
            f"The provided amount sample metrics UDFs, aggregate metric UDFs "
            f"and unit conversion factors must all be equal."
        )
    metric_list: List[MetricUdf] = []
    for metric_udf, aggregate_metric_udf, unit_conversion in zip(
        metric_udfs, aggregate_metric_udfs, unit_conversion_factor
    ):
        metric_list.append(
            MetricUdf(
                sample_metric_udf=metric_udf,
                aggregate_udf=aggregate_metric_udf,
                unit_conversion=float(unit_conversion),
            )
        )
    return metric_list


def aggregate_udf(
    source_artifacts: List[Artifact],
    source_udf: str,
    unit_conversion: float,
) -> float:
    """
    Aggregate the specified UDF value across all source artifacts.
    NOTE: It assumes that all UDF values are numeric.
    """
    aggregated_value: float = 0

    for source_artifact in source_artifacts:
        if not source_artifact.udf.get(source_udf):
            LOG.info(f"Artifact {source_artifact} has no value for '{source_udf}'. Skipping!")
            continue
        aggregated_value += float(source_artifact.udf.get(source_udf))

    return aggregated_value * unit_conversion


def aggregate_metric_for_artifacts(
    metric: MetricUdf,
    process_type: str,
    artifacts: List[Artifact],
    lims: Lims,
) -> None:
    """
    Aggregate the metric UDF in the specified MetricUdf object across the all the artifacts
    found for the given process type and list of input artifacts. The sums are
    then saved to the destination UDF on the sample level.
    NOTE: Will only fetch values for artifacts that have a 'PASSED' QC flag.
    """
    for artifact in artifacts:
        samples: List[Sample] = artifact.samples
        aggregated_result: float = 0
        for sample in samples:
            source_artifacts: List[Artifact] = lims.get_artifacts(
                samplelimsid=sample.id, process_type=process_type, qc_flag="PASSED"
            )
            aggregated_result += aggregate_udf(
                source_artifacts=source_artifacts,
                source_udf=metric.sample_metric_udf,
                unit_conversion=metric.unit_conversion,
            )
        for sample in samples:
            sample.udf[metric.aggregate_udf] = aggregated_result
            sample.put()


def aggregate_all_metrics(
    metrics: List[MetricUdf], process_type: str, artifacts: List[Artifact], lims: Lims
) -> None:
    """Aggregate all metric UDFs across all given input artifacts."""
    for metric in metrics:
        aggregate_metric_for_artifacts(
            metric=metric,
            process_type=process_type,
            artifacts=artifacts,
            lims=lims,
        )


@click.command()
@options.metric_udfs()
@options.aggregate_metric_udfs()
@options.unit_conversion()
@options.process_types()
@click.pass_context
def aggregate_sequencing_metrics(
    ctx,
    metric_udfs: List[str],
    aggregate_metric_udfs: List[str],
    unit_conversion_factor: List[str],
    process_types: List[str],
):
    """
    Script for aggregating artifact UDFs for numeric values and saving them to the sample level.
    Will skip all values coming from artifacts without a passed QC flag.
    """

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process: Process = ctx.obj["process"]
    lims: Lims = ctx.obj["lims"]

    try:
        metrics: List[MetricUdf] = create_metric_list(
            metric_udfs=metric_udfs,
            aggregate_metric_udfs=aggregate_metric_udfs,
            unit_conversion_factor=unit_conversion_factor,
        )
        artifacts: List[Artifact] = get_artifacts(process=process)
        for process_type in process_types:
            aggregate_all_metrics(
                metrics=metrics, process_type=process_type, artifacts=artifacts, lims=lims
            )
        click.echo("All UDF values have been aggregated!")
    except LimsError as e:
        sys.exit(e.message)
