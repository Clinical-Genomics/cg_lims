#!/usr/bin/env python
import logging
import sys
from pathlib import Path
from typing import List

import click
from genologics.lims import Artifact

from cg_lims import options
from cg_lims.EPPs.files.hamilton.models import BarcodeFileRow
from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.files.manage_csv_files import build_csv, sort_csv_plate_and_tube
from cg_lims.get.artifacts import get_artifacts

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
destination_barcodes: list = []


def get_barcode(artifact: Artifact) -> str:
    """Get the value/name of the container barcode"""
    return artifact.udf.get("Output Container Barcode")


def make_dest_barcode_list(destination_artifacts: List[Artifact]) -> list:
    """Create a list of all destination barcodes for all artifacts in the step."""
    for destination_artifact in destination_artifacts:
        destination_barcodes.append(get_barcode(destination_artifact))
    return destination_barcodes


def validate_set_barcode(barcode: str, artifact: Artifact, error_list: list) -> None:
    """Check that the container barcode is set for all artifacts."""
    if barcode is None:
        error_list.append(artifact.samples[0].id)


def validate_unique_barcodes(
    source_barcode: str,
    source_artifact: Artifact,
    destination_barcodes: list,
    error_list: list,
) -> None:
    """Check that the source container barcode is not the same as any of the destination container barcodes."""

    if source_barcode in destination_barcodes:
        LOG.warning(
            f"Source artifact {source_artifact.samples[0].id}'s barcode clashes with the output container barcode"
        )
        error_list.append((source_artifact.samples[0].id, source_barcode))


def get_file_data_and_write(
    destination_artifacts: List[Artifact], file: str, volume_udf: str, buffer_udf: str, pool: bool
):
    """Making a hamilton normalization file with sample and buffer volumes, source and destination barcodes and wells."""

    missing_udfs: list = []
    missing_source_barcode: list = []
    missing_destination_barcode: list = []
    clashing_barcode: list = []  # (source_id, source_barcode)
    file_rows: list = []

    destination_barcodes: list = make_dest_barcode_list(destination_artifacts=destination_artifacts)

    for destination_artifact in destination_artifacts:
        destination_barcode: str = get_barcode(destination_artifact)
        validate_set_barcode(
            barcode=destination_barcode,
            artifact=destination_artifact,
            error_list=missing_destination_barcode,
        )
        source_artifacts = destination_artifact.input_artifact_list()
        buffer = True
        for source_artifact in source_artifacts:
            source_barcode: str = get_barcode(source_artifact)
            validate_set_barcode(
                barcode=source_barcode, artifact=source_artifact, error_list=missing_source_barcode
            )
            validate_unique_barcodes(
                source_barcode=source_barcode,
                source_artifact=source_artifact,
                destination_barcodes=destination_barcodes,
                error_list=clashing_barcode,
            )

            try:
                row_data = BarcodeFileRow(
                    source_artifact=source_artifact,
                    destination_artifact=destination_artifact,
                    pool=pool,
                    buffer=buffer,
                    sample_volume=volume_udf,
                    buffer_volume=buffer_udf,
                )
                if pool:
                    buffer = False
            except:
                missing_udfs.append(source_artifact.samples[0].id)
                continue

            row_data_dict: dict = row_data.dict(by_alias=True)

            file_rows.append([row_data_dict[header] for header in HEADERS])

    build_csv(file=Path(file), rows=file_rows, headers=HEADERS)
    sort_csv_plate_and_tube(
        file=Path(file),
        plate_columns=["Barcode Source Container", "Source Well"],
        tube_columns=["Destination Well"],
        plate_well_columns=["Source Well"],
        tube_well_columns=["Destination Well"],
    )

    if missing_udfs:
        raise MissingUDFsError(
            f"All information was not added to the file. Udfs missing for samples: {', '.join(missing_udfs)}"
        )

    if missing_source_barcode or missing_destination_barcode or clashing_barcode:
        clash_descriptions: list = [
            f"{sample_id} with barcode {barcode}" for sample_id, barcode in clashing_barcode
        ]
        raise MissingUDFsError(
            f"Error concerning barcodes for the following one, two or three cases: \n"
            f"The following samples are missing the source barcode: {', '.join(missing_source_barcode)}. \n"
            f"The following samples are missing the destination barcode: {', '.join(missing_destination_barcode)}. \n"
            f"The following samples clash with the destination container barcodes. Please make sure the destination barcodes are unique! \n{', '.join(clash_descriptions)}."
        )


@click.command()
@options.file_placeholder(help="Hamilton Normalization File")
@options.buffer_udf()
@options.volume_udf()
@options.pooling_step()
@options.measurement()
@click.pass_context
def barcode_file(
    ctx: click.Context,
    file: str,
    volume_udf: str,
    buffer_udf: str,
    pooling_step: bool,
    measurement: bool = False,
):
    """Script to make a hamilton normalization file."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process = ctx.obj["process"]
    artifacts = get_artifacts(process=process, measurement=measurement)
    try:
        get_file_data_and_write(
            pool=pooling_step,
            destination_artifacts=artifacts,
            file=f"{file}-hamilton-normalization.csv",
            volume_udf=volume_udf,
            buffer_udf=buffer_udf,
        )
        click.echo("The file was successfully generated.")
    except LimsError as e:
        sys.exit(e.message)
