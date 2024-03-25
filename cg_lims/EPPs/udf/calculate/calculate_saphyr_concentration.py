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

def get_concentration(artifact: Artifact) -> List[float]: 
    """Returns a list of all concentration replicates called 
    Concentration 1 (ng/ul), Concentration 2 (ng/ul) and Concentration 3 (ng/ul) of an artifact."""
    udf_names = ["Concentration 1 (ng/ul)", "Concentration 2 (ng/ul)", "Concentration 3 (ng/ul)"]
    concentrations = []
    for name in udf_names:
        concentrations.append(artifact.udf.get(name))
    return concentrations

def calculate_average_concentration(concentrations: List) -> float:
    """Returns the average concentration of the list concentrations"""
    return np.mean(concentrations)

def calculate_cv(concentrations: List) -> float:
    """Calculates the coefficient of variance of the concentrations with the average concentration 
    that was retrieved from calculate_average_concentration"""
    
    average_concentration = np.mean(concentrations)
    std_deviation = np.std(concentrations)
    coefficient_variation = std_deviation / average_concentration
    return coefficient_variation

def set_average_and_cv(artifact: Artifact) -> None:
    """Calls on the previous functions get_concentration, calculate_average_concentration and calculate_cv 
    and updates the udfs Average concentration (ng/ul) and Coefficient of variation (CV) with the calculated values"""
    concentrations = get_concentration(artifact=artifact)
    average_concentration = calculate_average_concentration(concentrations=concentrations)
    coefficient_variation = calculate_cv(concentrations=concentrations)
    
    artifact.udf["Average concentration (ng/ul)"] = average_concentration
    artifact.udf["Coefficient of variation (CV)"] = coefficient_variation
    print(coefficient_variation)
    artifact.put()

def validate_udf_values(artifact: Artifact) -> bool:
    """A function checking whether a concentration in the list of concentrations for each artifact has a negative/no/zero value.
    Then the function returns the output as 'False' and logs all those sample IDs in the EPP log"""
    udf_names = ["Concentration 1 (ng/ul)", "Concentration 2 (ng/ul)", "Concentration 3 (ng/ul)"]
    output = True
    for name in udf_names:
        if not artifact.udf.get(name) or artifact.udf.get(name) < 0:
            output = False
            LOG.info(f"Sample {artifact.samples[0].id} has an invalid concentration value for {name}. Skipping.")
    return output


@click.command()
@click.pass_context
def calculate_saphyr_concentration(ctx) -> None:
    """Calculates and sets the average concentration and coefficient of variance based on three given concentrations.
    Returns a message if this worked well, and if there were negative/no/zero concentration values, there's an error message for this"""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process = ctx.obj["process"]

    try:
        artifacts: List[Artifact] = get_artifacts(process=process, measurement=True)
        failed_samples = 0
        for artifact in artifacts:
            if validate_udf_values(artifact=artifact) == False:
                failed_samples += 1
                continue
            set_average_and_cv(artifact=artifact)
        if failed_samples:
            raise MissingUDFsError(f"{failed_samples} samples have invalid concentration values (<= 0). See log for more information.")
        message = "The average concentration and coefficient of variance have been calculated."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
