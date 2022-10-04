import re
import logging
import sys
import click
import pandas as pd

from pathlib import Path
from typing import List
from genologics.lims import Artifact
from cg_lims import options
from cg_lims.exceptions import LimsError, InvalidValueError, MissingValueError
from cg_lims.get.artifacts import get_artifacts
from cg_lims.get.fields import get_barcode


LOG = logging.getLogger(__name__)

def get_data_and_write(
    artifacts: List[Artifact], 
    file: str,
):
    """Making a barcode csv file with sample names as barcode."""

    file_rows = []
    unexpected_container_type = 0
    failed_samples = []

    for artifact in artifacts:
        try:
            barcode = get_barcode(artifact)
            art_container_type = artifact.container.type.name

            if art_container_type.lower() != "tube":

                LOG.info(
                    f"Sample {barcode} does not have container type \"Tube\" therefore excluded."
                )
                continue
            
            
            #Function to get project nr and sample id
            f=lambda x: re.findall(r'\d+',x)
            
            file_rows.append([barcode, f(barcode)[0], int(f(barcode)[1])])
            #                           ^^^^^          ^^^^^^
            #  e.g.     ACC10001A1 =    10001             1 
        
        except:
            unexpected_container_type = + 1
            failed_samples.append(artifact.samples[0].id)

    if unexpected_container_type:
        failed_message = " ".join(map(str, failed_samples))
        raise InvalidValueError(
            f"The following samples are missing a container: {failed_message} of type \"Tube\"."
        )

    if file_rows == []:
        raise MissingValueError(
            f"Missing samples with container type \"Tube\"."
        )

    # Sort and create csv file.
    unfiltered_df = pd.DataFrame(
        data=file_rows, 
        index = None, 
        columns = [
            "Barcode",
            "Project",
            "id",
        ]
        ).sort_values(by=["Project","id"])
    
    # Filter off unwanted columns
    out = unfiltered_df["Barcode"]
    out.to_csv(Path(file), index=False)
    



@click.command()
@options.file_placeholder(help="Barcode Tubes")
@options.input()
@click.pass_context
def make_barcode_csv(
    ctx: click.Context, file: str, input: bool,
):
    """Script to make barcode for tubes"""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process = ctx.obj["process"]
    artifacts = get_artifacts(process=process, input=input)
    try:
        get_data_and_write(
            artifacts=artifacts,
            file=f"{file}-Barcode-Tubes.csv",
        )
        click.echo("The file was successfully generated.")
    except LimsError as e:
        sys.exit(e.message)
