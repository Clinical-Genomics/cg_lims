import logging
import sys
import click

from pathlib import Path
from typing import List
from genologics.lims import Artifact
from cg_lims import options
from cg_lims.exceptions import LimsError, InvalidValueError, MissingValueError
from cg_lims.files.manage_csv_files import build_csv
from cg_lims.get.artifacts import get_artifacts

LOG = logging.getLogger(__name__)

HEADERS = [
    "Barcodes"
]


def get_data_and_write(
    artifacts: List[Artifact], file: str,
):
    """Making a barcode csv file with sample names as barcode."""

    file_rows = []
    unexpected_container_type = 0
    failed_samples = []

    for artifact in artifacts:
        try:
            barcode = str(artifact.samples[0].id)
            container_type = str(artifact.container.type.name)

            if container_type.lower() != "tube":

                LOG.info(
                    f"Sample {barcode} does not have container type \"Tube\" therefore excluded"
                )
                continue

            file_rows.append([barcode])
        except:
            unexpected_container_type = + 1
            failed_samples.append(str(artifact.samples[0].id))

    if unexpected_container_type:
        failed_message = " ".join(map(str, failed_samples))
        raise InvalidValueError(
            f"The following samples are missing a container: {failed_message}"
        )

    if file_rows == []:
        raise MissingValueError(
            f"Missing samples with container type \"Tube\"."
        )

    build_csv(file=Path(file), rows=file_rows, headers=HEADERS)


@click.command()
@options.file_placeholder(help="Barcode Tubes")
@click.pass_context
def make_barcode_csv(
    ctx: click.Context, file: str
):
    """Script to make barcode for tubes"""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process = ctx.obj["process"]
    artifacts = get_artifacts(process=process, input=True)
    try:
        get_data_and_write(
            artifacts=artifacts,
            file=f"{file}-Barcode-Tubes.csv",
        )
        click.echo("The file was successfully generated.")
    except LimsError as e:
        sys.exit(e.message)
