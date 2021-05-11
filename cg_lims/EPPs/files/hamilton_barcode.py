#!/usr/bin/env python
import csv
import logging
import sys
from pathlib import Path
from typing import List

import click
from genologics.lims import Lims, Artifact
from pydantic import BaseModel, Field

from cg_lims import options
from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.files.make_csv import make_plate_file
from cg_lims.get.artifacts import get_artifacts, get_latest_artifact

LOG = logging.getLogger(__name__)

HEADERS = [
    "Source Labware",
    "Barcode Source Container",
    "Source Well",
    "Sample Volume",
    "Destination Labware",
    "Barcode Destination Container",
    "Destination Well",
    "Buffer Volume",
]


def build_csv(rows: List[List[str]], file_name: str, headers: List[str]) -> Path:
    """Build csv."""

    file = Path(file_name)
    with open(file_name, "w", newline="\n") as new_csv:
        wr = csv.writer(new_csv, delimiter=",")
        wr.writerow(headers)
        wr.writerows(rows)

    return file


class BarcodeFileRow(BaseModel):
    source_labware: str = Field(..., alias="Source Labware")
    barcode_source_container: str = Field(..., alias="Barcode Source Container")
    source_well: str = Field(..., alias="Source Well")
    volume: str = Field(..., alias="Sample Volume")
    destination_labware: str = Field(..., alias="Destination Labware")
    barcode_destination_container: str = Field(..., alias="Barcode Destination Container")
    destination_well: str = Field(..., alias="Destination Well")
    buffer_volume: str = Field(..., alias="Buffer Volume")

    class Config:
        allow_population_by_field_name = True


def get_file_data_and_write(
    lims: Lims, artifacts: List[Artifact], file: str, volume_udf: str, buffer_udf: str
):
    """Getting row data for hamilton file based on amount and reagent label"""

    failed_samples = []
    file_rows = []
    for artifact in artifacts:

        source_artifacts = artifact.input_artifact_list()
        pool: bool = len(source_artifacts) > 1

        for source_artifact in source_artifacts:
            try:
                row_data = BarcodeFileRow(
                    source_labware=source_artifact.location[0].type.name,
                    barcode_source_container=source_artifact.udf.get("Barcode"),
                    source_well=source_artifact.location[1].replace(":", ""),
                    volume=(
                        source_artifact.udf.get(volume_udf)
                        if pool
                        else artifact.udf.get(volume_udf)
                    ),
                    destination_labware=artifact.location[0].type.name,
                    barcode_destination_container=artifact.udf.get("Barcode"),
                    destination_well=artifact.location[1].replace(":", ""),
                    buffer_volume=artifact.udf.get(buffer_udf),
                )
            except:
                failed_samples.append(source_artifact.id)
                continue

            row_data_dict = row_data.dict(by_alias=True)
            file_rows.append([row_data_dict[header] for header in HEADERS])

    build_csv(file_name=file, rows=file_rows, headers=HEADERS)

    if failed_samples:
        raise MissingUDFsError(
            f"All samples were not added to the file. Udfs missing for samples: {', '.join(failed_samples)}"
        )


@click.command()
@options.file_placeholder(help="Hamilton Noramlization File")
@options.buffer_udf()
@options.volume_udf()
@click.pass_context
def make_hamilton_barcode_file(ctx: click.Context, file: str, volume_udf: str, buffer_udf: str):
    """Script to make a """

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process = ctx.obj["process"]
    lims = ctx.obj["lims"]
    artifacts = get_artifacts(process=process, input=False)
    try:
        get_file_data_and_write(
            lims=lims,
            artifacts=artifacts,
            file=f"{file}-hamilton-normalization.txt",
            volume_udf=volume_udf,
            buffer_udf=buffer_udf,
        )
        click.echo("The file was successfully generated.")
    except LimsError as e:
        sys.exit(e.message)
