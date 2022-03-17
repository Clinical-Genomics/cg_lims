import logging
import sys
import click

from typing import List, Tuple

from genologics.entities import Process
from genologics.lims import Lims

from cg_lims.get.artifacts import get_artifacts
from cg_lims.set.udfs import copy_udfs_to_artifacts
from cg_lims.exceptions import LimsError, MissingUDFsError

LOG = logging.getLogger(__name__)


def get_source_udf(process: Process) -> List[Tuple[str, str]]:
    copy_tasks = {}
    source_udfs = []
    for udf, value in process.udf.items():
        if 'Copy task' in udf:
            task_number, copy_type = udf.split('-')
            if task_number.strip() in copy_tasks.keys():
                copy_tasks[task_number.strip()][copy_type.strip()] = value
            else:
                copy_tasks[task_number.strip()] = {copy_type.strip(): value}
    for copy_task in copy_tasks:
        source_udfs.append((copy_tasks[copy_task]['Source Step'], copy_tasks[copy_task]['Source Field']))
    if not source_udfs:
        raise MissingUDFsError(f"Copy task udf missing for process {process.id}.")
    return source_udfs


def copy_source_udfs_to_artifacts(process: Process, lims: Lims) -> None:
    artifacts = get_artifacts(process=process, input=True)
    source_udfs = get_source_udf(process)
    for task in source_udfs:
        copy_udfs_to_artifacts(artifacts=artifacts,
                               process_types=[task[0]],
                               lims=lims,
                               udfs=[(task[1], task[1])],
                               qc_flag=True,
                               measurement=True,
                               )


@click.command()
@click.pass_context
def aggregate_qc_and_copy_fields(ctx) -> None:
    """Script to calculate and apply Average Size (bp) to a set of samples
    given a subset of their real size lengths. NTC samples are ignored in the calculations."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process = ctx.obj["process"]
    lims = ctx.obj["lims"]

    try:
        copy_source_udfs_to_artifacts(process=process, lims=lims)

        message = "UDFs were successfully copied!"
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
