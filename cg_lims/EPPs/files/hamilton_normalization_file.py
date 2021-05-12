#!/usr/bin/env python
import csv
import logging
import sys
from pathlib import Path
from typing import List, Optional

import click
from genologics.lims import Lims, Artifact
from pydantic import BaseModel, Field, validator

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
    source_artifact: Artifact
    destination_artifact: Artifact
    pool: bool
    source_labware: Optional[str] = Field(alias="Source Labware")
    barcode_source_container: Optional[str] = Field(alias="Barcode Source Container")
    source_well: Optional[str] = Field(alias="Source Well")
    sample_volume: str = Field(alias="Sample Volume")
    destination_labware: Optional[str] = Field(alias="Destination Labware")
    barcode_destination_container: Optional[str] = Field(alias="Barcode Destination Container")
    destination_well: Optional[str] = Field(alias="Destination Well")
    buffer_volume: str = Field(alias="Buffer Volume")

    @validator("barcode_source_container", always=True, pre=True)
    def set_barcode_source_container(cls, v, values: dict) -> Optional[str]:
        return values["source_artifact"].udf.get("Barcode")

    @validator("barcode_destination_container", always=True, pre=True)
    def set_barcode_destination_container(cls, v, values: dict) -> Optional[str]:
        return values["destination_artifact"].udf.get("Barcode")

    @validator("source_labware", always=True, pre=True)
    def set_source_labware(cls, v, values: dict) -> Optional[str]:
        return values["source_artifact"].location[0].type.name

    @validator("destination_labware", always=True, pre=True)
    def set_sdestination_labware(cls, v, values: dict) -> Optional[str]:
        return values["destination_artifact"].location[0].type.name

    @validator("sample_volume", always=True, pre=True)
    def set_sample_volume(cls, v, values: dict) -> str:
        if values["pool"]:
            return values["source_artifact"].udf.get(v)
        else:
            return values["destination_artifact"].udf.get(v)

    @validator("buffer_volume", always=True, pre=True)
    def set_buffer_volume(cls, v, values: dict) -> str:
        if values["pool"]:
            return 0
        else:
            return values["destination_artifact"].udf.get(v)

    @validator("source_well", always=True, pre=True)
    def set_source_well(cls, v, values: dict) -> str:
        if values["source_labware"] == "Tube":
            return values["barcode_source_container"]
        else:
            return values["source_artifact"].location[1].replace(":", "")

    @validator("destination_well", always=True, pre=True)
    def set_destination_well(cls, v, values: dict) -> str:
        if values["destination_labware"] == "Tube":
            return values["barcode_destination_container"]
        else:
            return values["destination_artifact"].location[1].replace(":", "")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        validate_assignment = True


def get_file_data_and_write(
    destination_artifacts: List[Artifact], file: str, volume_udf: str, buffer_udf: str, pool: bool
):
    """Making a hamilton normalization file with sample and buffer volumes, source and destination barcodes and wells."""

    failed_samples = []
    file_rows = []
    for destination_artifact in destination_artifacts:
        source_artifacts = destination_artifact.input_artifact_list()
        buffer_not_set = True
        for source_artifact in source_artifacts:
            try:
                row_data = BarcodeFileRow(
                    source_artifact=source_artifact,
                    destination_artifact=destination_artifact,
                    pool=pool,
                    sample_volume=volume_udf,
                    buffer_volume=buffer_udf,
                )
                if pool and buffer_not_set:
                    row_data.buffer_volume = destination_artifact.udf.get(buffer_udf)
                    buffer_not_set = False

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
@options.pooling_step()
@click.pass_context
def make_hamilton_barcode_file(
    ctx: click.Context, file: str, volume_udf: str, buffer_udf: str, pooling_step: bool
):
    """Script to make a hamilton normalization file"""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process = ctx.obj["process"]
    artifacts = get_artifacts(process=process, input=False)
    try:
        get_file_data_and_write(
            pool=pooling_step,
            destination_artifacts=artifacts,
            file=f"{file}-hamilton-normalization.txt",
            volume_udf=volume_udf,
            buffer_udf=buffer_udf,
        )
        click.echo("The file was successfully generated.")
    except LimsError as e:
        sys.exit(e.message)
