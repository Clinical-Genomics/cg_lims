import logging
import sys
import click

from pathlib import Path
from typing import List
from genologics.lims import Artifact
from cg_lims import options
from cg_lims.exceptions import LimsError, InvalidValueError, MissingValueError
from cg_lims.get.artifacts import get_artifacts

LOG = logging.getLogger(__name__)

def get_barcode_set_udf(
    artifacts: List[Artifact],
    artifact_udf: str,
    container_type: str,
):
    """Assigning barcode udf"""
    
    assigned_artifacts = 0
    unassigned_artifacts = 0
    total_artifacts = len(artifacts)
    unexpected_container_type = 0
    failed_samples = []

    for artifact in artifacts:
        try:
            barcode = str(artifact.samples[0].id)
            art_container_type = str(artifact.container.type.name)
            

            if art_container_type.lower() != container_type.lower():
                
                unassigned_artifacts += 1

                LOG.info(
                    f"Sample {barcode} does not have container type \"Tube\" therefore excluded"
                )
                continue

            else:
                artifact.udf[artifact_udf] = barcode
                artifact.put()
                assigned_artifacts += 1
                

        except:
            unexpected_container_type += 1
            failed_samples.append(str(artifact.samples[0].id))


    rest_check = total_artifacts - unassigned_artifacts - assigned_artifacts

    if unexpected_container_type:
        failed_message = ", ".join(map(str, failed_samples))
        raise InvalidValueError(
            f"Samples {failed_message} are missing udf container or udf \"{artifact_udf}\"."
        )
    
    elif rest_check:
        raise MissingValueError( f"There are {rest_check} samples with container type {container_type}.")
    
    elif not assigned_artifacts:
        raise MissingValueError( f"No barcode assigned.")

@click.command()
@options.artifact_udf(
    help="The name of the barcode udf."
)
@options.input()
@options.container_type()
@click.pass_context
def assign_tube_barcode(
    ctx: click.Context,
    artifact_udf: str,
    input: bool,
    container_type: str,
):
    """Script to make barcode for tubes"""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process = ctx.obj["process"]
    artifacts = get_artifacts(process=process, input=input)
    try:
        get_barcode_set_udf(
            artifacts=artifacts,
            artifact_udf=artifact_udf,
            container_type=container_type
        )
        click.echo("Barcodes were successfully generated.")
    except LimsError as e:
        sys.exit(e.message)
