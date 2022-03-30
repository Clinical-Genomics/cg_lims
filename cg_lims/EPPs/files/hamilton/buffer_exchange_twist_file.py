#!/usr/bin/env python

import logging
import sys

import click
from typing import List
from genologics.entities import Artifact

from cg_lims import options
from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.files.manage_csv_files import make_plate_file
from cg_lims.get.artifacts import get_artifacts
from cg_lims.get.fields import get_artifact_well
from cg_lims.get.samples import get_one_sample_from_artifact

LOG = logging.getLogger(__name__)


def get_file_data_and_write(artifacts: List[Artifact], file: str) -> None:
    """Getting row data for hamilton file from artifacts"""

    file_rows = {}
    for artifact in artifacts:
        well = get_artifact_well(artifact=artifact)
        if well == "11":
            message = "No well found for sample(s). Script does not work without a sample plate."
            LOG.error(message)
            raise MissingUDFsError(message=message)

        lims_id = get_one_sample_from_artifact(artifact=artifact).id

        barcode = artifact.udf.get("Input Container Barcode", "-")
        sample_volume = artifact.udf.get("Sample Volume (ul)", "-")
        beads_volume = artifact.udf.get("Volume Beads (ul)", "-")
        elution_volume = artifact.udf.get("Volume Elution (ul)", "-")

        file_rows[well] = [
            barcode,
            lims_id,
            well,
            sample_volume,
            beads_volume,
            elution_volume,
        ]

    headers = [
        "Input Plate Barcode",
        "LIMS ID",
        "Well ID",
        "Volume Sample",
        "Volume Beads",
        "Volume Elution buffer",
    ]

    make_plate_file(file, file_rows, headers)


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
def buffer_exchange_twist_file(ctx: click.Context, file: str, extension: str):
    """Script to make a csv file for hamilton for step Buffer Exchange TWIST. See AM doc #2125"""
    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process = ctx.obj["process"]
    artifacts = get_artifacts(process=process, input=False)

    file_name = (
        f"{file}_{artifacts[0].container.name}_{process.type.name.replace(' ', '_')}"
        f"{resolve_file_extension(extension)}"
    )

    try:
        get_file_data_and_write(artifacts, file_name)
        click.echo("The file was successfully generated.")
    except LimsError as e:
        sys.exit(e.message)
