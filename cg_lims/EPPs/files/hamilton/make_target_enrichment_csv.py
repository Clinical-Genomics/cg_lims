import logging
import sys

import click

from cg_lims import options
from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.files.manage_csv_files import make_plate_file
from cg_lims.get.artifacts import get_artifacts

LOG = logging.getLogger(__name__)


def get_file_data_and_write(artifacts: list, file: str) -> None:
    """Getting row data for Hamilton file"""

    failed_samples: list = []
    file_rows: dict = {}
    for artifact in artifacts:
        sample_id: str = artifact.name
        well: str = artifact.location[1].replace(":", "")
        bait_set: str = artifact.udf.get("Bait Set")
        pcr_plate: str = artifact.udf.get("PCR Plate")

        if not bait_set or not pcr_plate:
            failed_samples.append(sample_id)
            continue

        file_rows[well] = [sample_id, well, bait_set, pcr_plate]

    headers = [
        "LIMS ID",
        "Pool Well",
        "Bait Set",
        "PCR Plate",
    ]

    make_plate_file(file, file_rows, headers)

    if failed_samples:
        raise MissingUDFsError(
            f"Missing values for the UDFs Bait Set or PCR Plate for artifacts: {', '.join(failed_samples)}."
        )


def resolve_file_extension(extension: str) -> str:
    """Appends a period symbol to extension string if none is present. Otherwise, returns given extension string"""
    if extension:
        if extension.startswith("."):
            return extension
        return f".{extension}"
    return ""


@click.command()
@options.file_placeholder(help="Hamilton file.")
@options.file_extension()
@click.pass_context
def make_target_enrichment_csv(ctx: click.Context, file: str, extension: str):
    """Script to make a csv file for Target Enrichment on Hamilton."""
    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process = ctx.obj["process"]
    artifacts = get_artifacts(process=process, input=False)

    file_name: str = (
        f"{file}_{artifacts[0].container.name}_{process.type.name.replace(' ', '_')}"
        f"{resolve_file_extension(extension)}"
    )

    try:
        get_file_data_and_write(artifacts, file_name)
        click.echo("The file was successfully generated.")
    except LimsError as e:
        sys.exit(e.message)
