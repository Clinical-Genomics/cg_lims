import logging
import sys
import click

from typing import Dict, Literal, Any

from genologics.entities import Process
from genologics.lims import Lims

from cg_lims.get.artifacts import get_artifacts
from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.set.udfs import aggregate_qc_and_copy_udfs_to_artifacts

LOG = logging.getLogger(__name__)


def get_source_udf(
    process: Process,
) -> Dict[str, Dict[Literal["Source Step", "Source Field"], Any]]:
    copy_tasks = {}

    for udf, value in process.udf.items():
        if "Copy task" not in udf:
            continue
        task_number, copy_type = udf.split("-")
        print(task_number)
        task_number = task_number.strip()
        copy_type = copy_type.strip()
        if copy_type not in ["Source Step", "Source Field"]:
            raise MissingUDFsError(
                f'Copy type was: {copy_type}! Must be "Source Step" or "Source Field"'
            )
        if task_number in copy_tasks:
            copy_tasks[task_number][copy_type] = value
        else:
            copy_tasks[task_number] = {copy_type: value}

    return copy_tasks


def copy_source_udfs_to_artifacts(process: Process, lims: Lims) -> None:
    artifacts = get_artifacts(process=process, input=True)
    source_udfs: dict = get_source_udf(process)
    for nr, task in source_udfs.items():
        aggregate_qc_and_copy_udfs_to_artifacts(
            artifacts=artifacts,
            process_types=[task["Source Step"]],
            lims=lims,
            udfs=[(task["Source Field"], task["Source Field"])],
            qc_flag=True,
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
