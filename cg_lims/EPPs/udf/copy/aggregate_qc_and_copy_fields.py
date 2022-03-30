import logging
import sys
import click

from typing import List, Dict, Literal, Any

from genologics.entities import Process, Artifact
from genologics.lims import Lims

from cg_lims.get.artifacts import get_artifacts, outputs_per_input
from cg_lims.exceptions import LimsError, MissingUDFsError

LOG = logging.getLogger(__name__)


def get_copy_tasks(
    process: Process,
) -> Dict[str, Dict[Literal["Source Step", "Source Field"], Any]]:
    copy_tasks = {}

    for udf, value in process.udf.items():
        if "Copy task" not in udf:
            continue
        task_number, copy_type = udf.split("-")
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


def copy_source_udfs_to_artifacts(input_artifacts: List[Artifact], copy_tasks: dict, lims: Lims):
    failed_udfs = []
    for task_number, task in copy_tasks.items():
        for artifact in input_artifacts:
            processes = lims.get_processes(
                inputartifactlimsid=artifact.id, type=task["Source Step"]
            )
            udf = task["Source Field"]
            latest_process = get_latest_process(processes=processes)
            selected_outputs = outputs_per_input(
                input_artifact_id=artifact.id,
                process=latest_process,
                output_generation_type="PerInput",
                output_type="ResultFile",
            )
            output = selected_outputs[0]  # supposed to be only one here
            output = Artifact(lims=lims, id=output.id)
            qc_flag_update = output.qc_flag
            if qc_flag_update == "UNKNOWN":
                continue
            if artifact.qc_flag != "FAILED":
                artifact.qc_flag = qc_flag_update

            value = output.udf.get(udf)
            if value is None:
                failed_udfs.append(artifact.name)
                continue
            try:
                artifact.udf[udf] = float(value)
            except:
                artifact.udf[udf] = str(value)

            artifact.put()


def get_latest_process(processes: List[Process]) -> Process:
    if not processes:
        raise
    latest_process = processes[0]
    for process in processes:
        if latest_process.date_run < process.date_run:
            latest_process = process
    return latest_process


@click.command()
@click.pass_context
def aggregate_qc_and_copy_fields(ctx) -> None:
    """Script to calculate and apply Average Size (bp) to a set of samples
    given a subset of their real size lengths. NTC samples are ignored in the calculations."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process = ctx.obj["process"]
    lims = ctx.obj["lims"]

    try:
        artifacts: List[Artifact] = get_artifacts(process=process, input=True)
        copy_tasks = get_copy_tasks(process=process)
        copy_source_udfs_to_artifacts(input_artifacts=artifacts, copy_tasks=copy_tasks, lims=lims)
        message = "UDFs were successfully copied!"
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
