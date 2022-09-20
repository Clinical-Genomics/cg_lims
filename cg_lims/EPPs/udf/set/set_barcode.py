import logging
import sys
import click

from pathlib import Path
from typing import List
from genologics.lims import Artifact
from cg_lims import options
from cg_lims.exceptions import LimsError, InvalidValueError, MissingValueError
from cg_lims.get.artifacts import get_artifacts
from cg_lims.get.fields import get_barcode

LOG = logging.getLogger(__name__)

def get_barcode_set_udf(
    artifacts: List[Artifact],
    artifact_udf: str,
    container_type: str,
):

    """Assigning barcode to a barcode udf.
    
    - Assigned on container type if selected.
    - Gives warning if no samples assigned.
    - Checks if script failed and what the cause might be.
    - Informs user if sample doesn't have a defined barcode.

    """
    
    assigned_artifacts = 0
    failed_artifact = 0
    failed_samples = []

    for artifact in artifacts:
        try:
            art_container_type = str(artifact.container.type.name)
            
            # Removes all incorrect container types if option is used. 
            if container_type:
                if art_container_type.lower() != container_type.lower():

                    LOG.info(
                        f"Sample {str(artifact.samples[0].id)} does not have container type {container_type} therefore excluded"
                    )
                    continue

                # Sample has the correct "container_type".
                else:
                    barcode = get_barcode(artifact)

                    if barcode != "" and barcode != "-" and barcode != None:
                        artifact.udf[artifact_udf] = barcode
                        artifact.put()
                        assigned_artifacts += 1
                    
                    # Triggered if barcode is not defined (i.e empty string).
                    else:
                        LOG.info(
                        f"Sample {str(artifact.samples[0].id)} does not have defined barcode therefore excluded"
                        )

            # Get all barcode to all samples.
            else:
                barcode = get_barcode(artifact)

                if barcode != "" and barcode != "-" and barcode != None:
                    artifact.udf[artifact_udf] = barcode
                    artifact.put()
                    assigned_artifacts += 1
                
                # Triggered if barcode is not defined (i.e empty string).
                else:
                    LOG.info(
                    f"Sample {str(artifact.samples[0].id)} does not have defined barcode therefore excluded"
                    )

        # Collects failed samples.
        except:
            failed_artifact += 1
            failed_samples.append(str(artifact.samples[0].id))

    # Triggered if any failed samples.
    if failed_artifact:
        failed_message = ", ".join(map(str, failed_samples))
        raise InvalidValueError(
            f"Samples {failed_message}, are missing udf container or udf \"{artifact_udf}\"."
        )
    
    # Notifies that no sample got a barcode.
    elif not assigned_artifacts:
        raise MissingValueError( f"No barcode assigned. Check parameters.")

@click.command()
@options.artifact_udf(
    help="The name of the barcode udf."
)
@options.input()
@options.container_type()
@click.pass_context
def assign_barcode(
    ctx: click.Context,
    artifact_udf: str,
    input: bool,
    container_type: str,
):
    """Assigned barcode to UDF"""

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
