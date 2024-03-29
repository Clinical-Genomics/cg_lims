import logging
import sys
from typing import List

import click
import numpy as np
from cg_lims import options
from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts
from genologics.entities import Artifact

LOG = logging.getLogger(__name__)


def get_concentrations(artifact: Artifact, udf_names: List[str]) -> List[float]:
    """Returns a list of all concentration replicates of an artifact."""
    concentrations = []
    for name in udf_names:
        concentrations.append(artifact.udf.get(name))
    return concentrations


def calculate_average_concentration(concentrations: List[float]) -> float:
    """Returns the average concentration of the list concentrations"""
    return float(np.mean(concentrations))


def calculate_cv(concentrations: List[float]) -> float:
    """Calculates the coefficient of variance of the concentrations with the average concentration
    that was retrieved from calculate_average_concentration"""
    average_concentration = np.mean(concentrations)
    std_deviation = np.std(concentrations)
    coefficient_variation = std_deviation / average_concentration
    return coefficient_variation


def set_average_and_cv(artifact: Artifact, udf_names: List[str]) -> None:
    """Calls on the previous functions get_concentration, calculate_average_concentration and calculate_cv
    and updates the UDFs Average concentration (ng/ul) and Coefficient of variation (CV) with the calculated values
    """
    concentrations = get_concentrations(artifact=artifact, udf_names=udf_names)
    average_concentration = calculate_average_concentration(concentrations=concentrations)
    coefficient_variation = calculate_cv(concentrations=concentrations)

    artifact.udf["Average concentration (ng/ul)"] = average_concentration
    artifact.udf["Coefficient of variation (CV)"] = coefficient_variation
    artifact.put()


def validate_udf_values(artifact: Artifact, udf_names: List[str]) -> bool:
    """A function checking whether a concentration in the list of concentrations for each artifact has a negative/no/zero value.
    Then the function returns the output as 'False' and logs all those sample IDs in the EPP log"""
    output = True
    for name in udf_names:
        if not artifact.udf.get(name) or artifact.udf.get(name) < 0:
            output = False
            LOG.info(
                f"Sample {artifact.samples[0].id} has an invalid concentration value for {name}. Skipping."
            )
    return output


@click.command()
@options.concentration_replicates()
@click.pass_context
def calculate_saphyr_concentration(ctx, concentration_udf: List[str]) -> None:
    """Calculates and sets the average concentration and coefficient of variance based on three given concentrations.
    Returns a message if this worked well, and if there were negative/no/zero concentration values, there's an error message for this
    """

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process = ctx.obj["process"]

    try:
        artifacts: List[Artifact] = get_artifacts(process=process, measurement=True)
        failed_samples = 0
        for artifact in artifacts:
            if not validate_udf_values(artifact=artifact, udf_names=concentration_udf):
                failed_samples += 1
                continue
            set_average_and_cv(artifact=artifact, udf_names=concentration_udf)
        if failed_samples:
            raise MissingUDFsError(
                f"{failed_samples} samples have invalid concentration values (<= 0). See log for more information."
            )
        message = "The average concentration and coefficient of variance have been calculated for all samples."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
