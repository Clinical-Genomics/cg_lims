import logging
import sys
import click
import numpy as np

from typing import List

from genologics.entities import Artifact

from cg_lims import options
from cg_lims.get.artifacts import get_artifacts
from cg_lims.exceptions import LimsError, MissingUDFsError

LOG = logging.getLogger(__name__)


def calculate_average_size(all_artifacts: List[Artifact]) -> float:
    """Calculate average size (bp) from given list of artifacts.
    Returns the average and number of missing UDF:s."""

    artifacts = [artifact for artifact in all_artifacts if artifact.name[0:3] != "NTC"]
    size_list = [
        artifact.udf["Size (bp)"]
        for artifact in artifacts
        if artifact.udf.get("Size (bp)") is not None
    ]

    if not size_list:
        raise MissingUDFsError("Udf missing for 'Size (bp)' sample(s).")
    return float(np.mean(size_list))


def set_average_and_qc(
    average: float,
    lower_threshold: str,
    upper_threshold: str,
    all_artifacts: List[Artifact],
) -> None:
    """Sets the given average to a list of artifacts.
    Also assesses QC flags according to defined thresholds."""
    qc_flag = "PASSED"
    if lower_threshold is not None and int(average) < int(lower_threshold):
        qc_flag = "FAILED"
    elif upper_threshold and int(average) > int(upper_threshold):
        qc_flag = "FAILED"

    for artifact in all_artifacts:
        artifact.udf["Average Size (bp)"] = str(average)
        if artifact.qc_flag != "FAILED":
            artifact.qc_flag = qc_flag
        artifact.put()


@click.command()
@options.lower_threshold()
@options.upper_threshold()
@click.pass_context
def calculate_average_size_and_set_qc(ctx, lower_threshold: str, upper_threshold: str) -> None:
    """Script to calculate and apply Average Size (bp) to a set of samples
    given a subset of their real size lengths. NTC samples are ignored in the calculations."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process = ctx.obj["process"]

    try:
        artifacts: List[Artifact] = get_artifacts(process=process, input=True)
        average: float = calculate_average_size(all_artifacts=artifacts)
        set_average_and_qc(
            average=average,
            lower_threshold=lower_threshold,
            upper_threshold=upper_threshold,
            all_artifacts=artifacts,
        )
        message = "Average Size (bp) have been calculated and set for all samples."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
