import logging
import sys
from datetime import date
from typing import List

import click
import numpy as np
from cg_lims.exceptions import InvalidValueError, LimsError
from cg_lims.get.artifacts import get_artifacts, get_latest_artifact, get_non_pooled_artifacts
from genologics.entities import Artifact, Container, Process
from genologics.lims import Lims

LOG = logging.getLogger(__name__)


def get_run_name(process: Process) -> str:
    """Create and return a run name from today's date and the step ID."""
    return f"{date.today().strftime('%y%m%d')}_{process.id}"


def set_run_name(process: Process) -> None:
    """Set the run name to both process and artifact UDFs."""
    run_name: str = get_run_name(process=process)
    process.udf["Run Name"] = run_name
    process.put()


def set_plates(process: Process) -> None:
    """Sets default values for the plates in the step."""
    containers: List[Container] = process.output_containers()
    containers.sort(key=lambda container_object: container_object.id)
    if len(containers) > 2:
        raise InvalidValueError(
            f"Error: The maximum number of plates you can have for a sequencing run is 2!"
        )
    i = 1
    for container in containers:
        process.udf[f"Plate {i}"] = container.name
        i += 1
    process.put()


def calculate_weighted_average_size(artifact: Artifact) -> float:
    """"""
    if len(artifact.samples) <= 1:
        input_artifact = artifact.input_artifact_list()[0]
        return input_artifact.udf.get("Size (bp)")
    input_artifacts: List[Artifact] = get_non_pooled_artifacts(artifact=artifact)
    sizes: List[float] = []
    volumes: List[float] = []
    for input_artifact in input_artifacts:
        sizes.append(input_artifact.udf.get("Size (bp)"))
        volumes.append(input_artifact.udf.get("Volume of sample (ul)"))
    return round(np.average(sizes, weights=volumes), 0)


def get_library_concentration(artifact: Artifact) -> float:
    """"""
    lims: Lims = artifact.lims
    sample_id: str = artifact.samples[0].id
    if len(artifact.samples) <= 1:
        udf_name: str = "Loading Concentration (pM)"
        step_name: str = "Preparing ABC Complex (Revio)"
    else:
        udf_name: str = "Target Pool Concentration (pM)"
        step_name: str = "Pooling Samples for Sequencing (Revio)"
    all_artifacts = lims.get_artifacts(process_type=step_name, samplelimsid=sample_id)
    artifact: Artifact = get_latest_artifact(lims_artifacts=all_artifacts)
    parent_process: Process = artifact.parent_process
    return parent_process.udf[udf_name]


def get_polymerase_kit(artifact: Artifact) -> float:
    """"""
    lims: Lims = artifact.lims
    sample_id: str = artifact.samples[0].id
    all_artifacts = lims.get_artifacts(
        process_type="Preparing ABC Complex (Revio)", samplelimsid=sample_id
    )
    artifact: Artifact = get_latest_artifact(lims_artifacts=all_artifacts)
    parent_process: Process = artifact.parent_process
    return parent_process.udf["Binding Kit"]


def set_artifact_values(artifacts: List[Artifact]) -> None:
    """"""
    for artifact in artifacts:
        artifact.udf["Mean Size (bp)"] = calculate_weighted_average_size(artifact=artifact)
        artifact.udf["Library Concentration (pM)"] = get_library_concentration(artifact=artifact)
        artifact.udf["Polymerase Kit"] = get_polymerase_kit(artifact=artifact)
        artifact.put()


@click.command()
@click.pass_context
def set_revio_sequencing_settings(ctx):
    """Sets the values required for sequencing of Revio SMRT cells."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process: Process = ctx.obj["process"]

    try:
        artifacts: List[Artifact] = get_artifacts(process=process)
        set_run_name(process=process)
        set_plates(process=process)
        set_artifact_values(artifacts=artifacts)
        message: str = "Revio sequencing settings have been successfully set."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
