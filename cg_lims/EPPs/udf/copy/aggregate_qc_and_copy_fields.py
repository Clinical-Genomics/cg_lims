import logging
import sys
import click

from typing import List, Tuple, Optional

from genologics.entities import Artifact, Process
from genologics.lims import Lims

from cg_lims.get.artifacts import get_artifacts, get_qc_output_artifacts, get_latest_artifact
from cg_lims.get.udfs import get_process_udf
from cg_lims.EPPs.udf.copy.artifact_to_artifact import copy_udfs_to_all_artifacts
from cg_lims.set.udfs import copy_artifact_to_artifact
from cg_lims.exceptions import LimsError, MissingUDFsError

LOG = logging.getLogger(__name__)


def get_source_udf(process: Process) -> List[Tuple[str, str]]:
    copy_task_1_step = get_process_udf(process, "Copy task 1 - Source Step")
    copy_task_2_step = get_process_udf(process, "Copy task 2 - Source Step")
    copy_task_1_field = get_process_udf(process, "Copy task 1 - Source Field")
    copy_task_2_field = get_process_udf(process, "Copy task 2 - Source Field")
    source_udfs = [(copy_task_1_step, copy_task_1_field), (copy_task_2_step, copy_task_2_field)]
    return source_udfs


def get_latest_processes(artifact: Artifact, process_type: str, lims: Lims) -> Process:
    """Get the lastest process of a specific type given an artifact"""
    processes = lims.get_processes(inputartifactlimsid=artifact.id)
    latest_process = ''
    for process in processes:
        current_process_type = process.type.name
        if current_process_type == process_type:
            if latest_process == '':
                latest_process = process
            elif latest_process.date_run < process.date_run:
                latest_process = process
    return latest_process


def copy_udfs(artifacts: List[Artifact], source_udfs: List[Tuple[str, str]], lims: Lims) -> None:
    for artifact in artifacts:
        source_processes = []
        for source
        = get_latest_processes(artifact=artifact, process_type: str, lims=lims)


@click.command()
@click.pass_context
def aggregate_qc_and_copy_fields(ctx) -> None:
    """Script to calculate and apply Average Size (bp) to a set of samples
    given a subset of their real size lengths. NTC samples are ignored in the calculations."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process = ctx.obj["process"]
    lims = ctx.obj["lims"]

    try:
        artifacts = get_artifacts(process=process, input=True) #check up
        print(artifacts)
        source_udfs = get_source_udf(process)
        latest_process = get_latest_processes(artifact=artifacts[0], process_type=source_udfs[0][0], lims=lims)
        print(latest_process)
        for task in source_udfs:
            print(task)
            copy_udfs_to_all_artifacts(artifacts=artifacts,
                                       process_types=[task[0]],
                                       lims=lims,
                                       udfs=[(task[1], task[1])],
                                       qc_flag=True,
                                       )

        message = "UDFs were successfully copied!"
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
