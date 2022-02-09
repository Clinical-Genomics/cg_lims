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


def calculate_average_and_qc(all_artifacts: List[Artifact], lower_threshold: int, upper_threshold: int) -> None:
    size_list = []
    missing_udf_count = 0
    artifacts = []

    for artifact in all_artifacts:
        if not artifact.name[0:3] == 'NTC':
            artifacts.append(artifact)

    for artifact in artifacts:
        try:
            size_list.append(int(artifact.udf['Size (bp)']))
        except:
            missing_udf_count += 1
            pass
    if size_list:
        average = np.mean(size_list)
    else:
        sys.exit("Set 'Size (bp)' for at least one sample")

    if lower_threshold is not None and int(average) < lower_threshold:
        qc_flag = 'FAILED'
    elif upper_threshold and int(average) > upper_threshold:
        qc_flag = 'FAILED'
    else:
        qc_flag = 'PASSED'

    for artifact in all_artifacts:
        artifact.udf['Average Size (bp)'] = str(average)
        if artifact.qc_flag == 'PASSED':
            artifact.qc_flag = qc_flag
        artifact.put()

    if missing_udf_count:
        raise MissingUDFsError(
            f"Udf missing for {missing_udf_count} sample(s). Average size was calculated without taking account to them."
        )


@click.command()
@options.lower_threshold()
@options.upper_threshold()
@click.pass_context
def calculate_average_size_and_set_qc(ctx, lower_threshold: int, upper_threshold: int) -> None:
    """Script to calculate and apply Average Size (bp) to a set of samples
     given a subset of their real size lengths. NTC samples are ignored in the calculations."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process = ctx.obj["process"]

    try:
        artifacts = get_artifacts(process=process, input=True)
        calculate_average_and_qc(
            all_artifacts=artifacts,
            lower_threshold=lower_threshold,
            upper_threshold=upper_threshold
        )
        message = "Average Size (bp) have been calculated and set for all samples."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
