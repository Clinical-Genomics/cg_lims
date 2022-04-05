#!/usr/bin/env python
import logging
import sys

import click
from cg_lims.get.processes import get_latest_process
from genologics.entities import Process, Artifact
from genologics.lims import Lims

from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts
from typing import List, Dict, Literal, Any


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
    if copy_tasks == {}:
        raise MissingUDFsError(f"Copy task UDF missing for process {process.id}")
    return copy_tasks


def copy_udfs(input_artifacts: List[Artifact], copy_tasks: dict, lims: Lims):
    """Loop through all artifacts and copy udfs from the corect steps."""
    failed_udfs = []
    process_types = [task["Source Step"] for task_number, task in copy_tasks.items()]
    process_types = list(set(process_types))
    for artifact in input_artifacts:
        artifact.get()
        source_steps = get_correct_steps_for_the_artifact(
            process_types=process_types, artifact=artifact, lims=lims
        )
        for process_type, source_step in source_steps.items():
            for output in source_step.outputs_per_input(artifact.id):
                qc_flag_update = Artifact(lims, id=output.id).qc_flag
                if not qc_flag_update or qc_flag_update == "UNKNOWN":
                    continue
                if artifact.qc_flag != "FAILED":
                    artifact.qc_flag = qc_flag_update
                for task_number, task in copy_tasks.items():
                    if task["Source Step"] != process_type:
                        continue
                    udf = task["Source Field"]
                    udf_value = output.udf.get(udf)
                    if udf_value is None:
                        failed_udfs.append(artifact.name)
                        continue
                    try:
                        artifact.udf[udf] = float(udf_value)
                    except:
                        artifact.udf[udf] = str(udf_value)

        artifact.put()


def get_correct_steps_for_the_artifact(
    process_types: List[str], artifact: Artifact, lims: Lims
) -> Dict[str, Process]:
    """Get the latest processes of the specified process types."""

    source_steps = {}
    processes = lims.get_processes(inputartifactlimsid=artifact.id, type=process_types)
    for process in processes:
        process_type = process.type.name
        if process_type in source_steps:
            source_steps[process_type] = get_latest_process([source_steps[process_type], process])
        else:
            source_steps[process_type] = process
    return source_steps


@click.command()
@click.pass_context
def aggregate_qc_and_copy_fields(ctx):
    """Script to copy artifact udf to sample udf"""

    process = ctx.obj["process"]
    lims = ctx.obj["lims"]
    try:
        copy_tasks = get_copy_tasks(process=process)
        artifacts = get_artifacts(process=process, input=True)
        copy_udfs(input_artifacts=artifacts, copy_tasks=copy_tasks, lims=lims)
        click.echo("Udfs have been set on all samples.")
    except LimsError as e:
        sys.exit(e.message)
