import logging
import sys
from datetime import date
from typing import List

import click
import numpy as np
from cg_lims.exceptions import InvalidValueError, LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts
from genologics.entities import Artifact, Container, Process

LOG = logging.getLogger(__name__)


def get_run_name() -> str:
    """Create and return a run name from today's date and the step ID."""
    return f"Run{date.today().strftime('%y%m%d')}"


def set_run_name(process: Process) -> None:
    """Set the run name to both process and artifact UDFs."""
    run_name: str = get_run_name()
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
    """Calculate the weighted average fragment size of an artifact (single sample or pool)"""
    input_artifacts: List[Artifact] = artifact.input_artifact_list()[0].input_artifact_list()
    sizes: List[float] = []
    volumes: List[float] = []
    for input_artifact in input_artifacts:
        sizes.append(input_artifact.udf.get("Size (bp)"))
        volumes.append(input_artifact.udf.get("Volume of sample (ul)"))
    return round(np.average(sizes, weights=volumes), 0)


def get_loading_concentration(artifact: Artifact) -> float:
    """Return the library concentration of an artifact"""
    input_artifact: Artifact = artifact.input_artifact_list()[0]
    loading_concentration: float = input_artifact.udf.get("Loading Concentration (pM)")
    if not loading_concentration:
        raise MissingUDFsError(
            f"Artifact {input_artifact.name} is missing a loading concentration!"
        )
    return loading_concentration


def set_artifact_values(artifacts: List[Artifact]) -> None:
    """Set all values needed for the artifacts in a Set Up Sequencing Run (Revio) step"""
    for artifact in artifacts:
        artifact.udf["Mean Size (bp)"] = calculate_weighted_average_size(artifact=artifact)
        artifact.udf["Library Concentration (pM)"] = get_loading_concentration(artifact=artifact)
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
