import logging
import sys
from typing import List

import click
from cg_lims import options
from cg_lims.exceptions import ArgumentError, LimsError
from cg_lims.get.artifacts import get_artifacts
from genologics.entities import Artifact, Entity, Process
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
    """"""
    if len(metric_udfs) != len(aggregate_metric_udfs) != len(unit_conversion_factor):
        raise ArgumentError(
            f"The provided amount sample metrics UDFs, aggregate metric UDFs "
            f"and unit conversion factors must all be equal."
        )
    metric_list = []
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
    destination_entity: Entity,
    destination_udf: str,
    unit_conversion: float,
) -> None:
    """"""
    aggregated_value: float = 0
    found_values: int = 0
    for source_artifact in source_artifacts:
        if not source_artifact.udf.get(source_udf):
            LOG.info(f"Artifact {source_artifact} has no value for '{source_udf}'. Skipping!")
            continue
        aggregated_value += float(source_artifact.udf.get(source_udf))
        found_values += 1
    if found_values:
        destination_entity.udf[destination_udf] = aggregated_value * unit_conversion
    else:
        LOG.warning(
            f"No matching '{source_udf}' values found for {destination_entity}. Nothing will be aggregated."
        )


def aggregate_values_for_artifact(
    metrics: List[MetricUdf],
    process_type: str,
    artifact: Artifact,
    lims: Lims,
) -> None:
    """"""
    for sample in artifact.samples:
        source_artifacts: List[Artifact] = lims.get_artifacts(
            samplelimsid=sample.id, process_type=process_type, qc_flag="PASSED"
        )
        for metric in metrics:
            aggregate_udf(
                source_artifacts=source_artifacts,
                source_udf=metric.sample_metric_udf,
                destination_entity=sample,
                destination_udf=metric.aggregate_udf,
                unit_conversion=metric.unit_conversion,
            )
        sample.put()


def aggregate_all_artifacts(
    metrics: List[MetricUdf], process_type: str, artifacts: List[Artifact], lims: Lims
) -> None:
    """"""
    for artifact in artifacts:
        aggregate_values_for_artifact(
            metrics=metrics,
            process_type=process_type,
            artifact=artifact,
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
    """"""

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
            aggregate_all_artifacts(
                metrics=metrics, process_type=process_type, artifacts=artifacts, lims=lims
            )
        click.echo("All UDF values have been aggregated!")
    except LimsError as e:
        sys.exit(e.message)
