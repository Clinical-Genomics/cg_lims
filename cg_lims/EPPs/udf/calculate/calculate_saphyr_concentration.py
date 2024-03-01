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
    """Returns a list of all concentration replicates of an artifact."""
    
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
    
    concentrations = get_concentration(artifact=artifact)
    average_concentration = calculate_average_concentration(concentrations=concentrations)
    coefficient_variation = calculate_cv(concentrations=concentrations)
    
    artifact.udf["Average concentration (ng/ul)"] = average_concentration
    artifact.udf["Coefficient of variation (CV)"] = coefficient_variation
    artifact.put()

@click.command()
@click.pass_context
def calculate_saphyr_concentration(ctx) -> None:

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process = ctx.obj["process"]

    try:
        artifacts: List[Artifact] = get_artifacts(process=process, measurement=True)
        for artifact in artifacts:
            set_average_and_cv(artifact=artifact)
        message = "The average concentration and coefficient of variance have been calculated."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
        