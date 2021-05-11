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
from cg_lims.files.manage_csv_files import make_plate_file, build_csv, sort_csv
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


class BarcodeFileRow(BaseModel):
    source_labware: str = Field(..., alias="Source Labware")
    barcode_source_container: str = Field(..., alias="Barcode Source Container")
    source_well: str = Field(..., alias="Source Well")
    sample_volume: str = Field(..., alias="Sample Volume")
    destination_labware: str = Field(..., alias="Destination Labware")
    barcode_destination_container: str = Field(..., alias="Barcode Destination Container")
    destination_well: str = Field(..., alias="Destination Well")
    buffer_volume: str = Field(..., alias="Buffer Volume")

    class Config:
        allow_population_by_field_name = True


def get_file_data_and_write(
    lims: Lims, destination_artifacts: List[Artifact], file: str, volume_udf: str, buffer_udf: str
):
    """Making a hamilton normalization file with sample and buffer volumes, source and destination barcodes and wells.

    If the script is being used in a pooling step (pool=True), the sample volume is fetched from input artifact,
    otherwise output artifact."""

    failed_samples = []
    file_rows = []
    for destination_artifact in destination_artifacts:
        source_artifacts = destination_artifact.input_artifact_list()
        pool: bool = len(source_artifacts) > 1
        pool_buffer_set = False
        for source_artifact in source_artifacts:
            try:
                if pool:
                    sample_volume = source_artifact.udf.get(volume_udf)
                    if pool_buffer_set:
                        buffer_volume = 0
                    else:
                        buffer_volume = destination_artifact.udf.get(buffer_udf)
                        pool_buffer_set = True
                else:
                    sample_volume = destination_artifact.udf.get(volume_udf)
                    buffer_volume = destination_artifact.udf.get(buffer_udf)

                barcode_source_container = source_artifact.udf.get("Barcode")
                barcode_destination_container = destination_artifact.udf.get("Barcode")

                source_labware = source_artifact.location[0].type.name
                destination_labware = destination_artifact.location[0].type.name

                if source_labware == "Tube":
                    source_well = barcode_source_container
                else:
                    source_well = source_artifact.location[1].replace(":", "")

                if destination_labware == "Tube":
                    destination_well = barcode_destination_container
                else:
                    destination_well = destination_artifact.location[1].replace(":", "")

                row_data = BarcodeFileRow(
                    source_labware=source_labware,
                    barcode_source_container=barcode_source_container,
                    source_well=source_well,
                    sample_volume=sample_volume,
                    destination_labware=destination_labware,
                    barcode_destination_container=barcode_destination_container,
                    destination_well=destination_well,
                    buffer_volume=buffer_volume,
                )
            except:
                failed_samples.append(source_artifact.id)
                continue

            row_data_dict = row_data.dict(by_alias=True)
            file_rows.append([row_data_dict[header] for header in HEADERS])

    build_csv(file=Path(file), rows=file_rows, headers=HEADERS)
    sort_csv(
        file=Path(file), columns=["Barcode Source Container", "Source Well", "Destination Well"]
    )

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
    """Script to make a hamilton normalization file"""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process = ctx.obj["process"]
    lims = ctx.obj["lims"]
    artifacts = get_artifacts(process=process, input=False)
    try:
        get_file_data_and_write(
            lims=lims,
            destination_artifacts=artifacts,
            file=f"{file}-hamilton-normalization.txt",
            volume_udf=volume_udf,
            buffer_udf=buffer_udf,
        )
        click.echo("The file was successfully generated.")
    except LimsError as e:
        sys.exit(e.message)
