#!/usr/bin/env python
import logging
import sys
from pathlib import Path
from typing import List

import click
from cg_lims import options
from cg_lims.EPPs.files.hamilton.models import BarcodeFileRow
from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.files.manage_csv_files import build_csv, sort_csv_plate_and_tube
from cg_lims.get.artifacts import get_artifacts
from genologics.lims import Artifact, Process

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


def get_barcode(artifact: Artifact) -> str:
    """Get the value/name of the container barcode"""
    return artifact.udf.get("Output Container Barcode")


def make_dest_barcode_list(destination_artifacts: List[Artifact]) -> List[str]:
    """Create a list of all destination barcodes for all artifacts in the step."""
    destination_barcodes: List[str] = []

    for destination_artifact in destination_artifacts:
        destination_barcodes.append(get_barcode(destination_artifact))
    return destination_barcodes


def validate_set_barcode(artifact: Artifact, error_list: List[str]) -> None:
    """Check that the container barcode is set for all artifacts."""
    barcode: str = get_barcode(artifact)
    if barcode is None:
        error_list.append(artifact.samples[0].id)


def validate_unique_barcodes(
    source_artifact: Artifact,
    destination_barcodes: List[str],
    clashing_barcodes: List[str],
) -> None:
    """Check that the source container barcode is not the same as any of the destination container barcodes."""

    source_barcode: str = get_barcode(source_artifact)
    if source_barcode in destination_barcodes:
        LOG.warning(
            f"Sample {source_artifact.samples[0].id}'s input barcode clashes with the output container barcode"
        )
        clashing_barcodes.append(source_barcode)


def get_file_data_and_write(
    destination_artifacts: List[Artifact], file: str, volume_udf: str, buffer_udf: str, pool: bool
):
    """Making a Hamilton normalization file with sample and buffer volumes, source and destination barcodes and wells."""

    missing_file_udfs: List[str] = []
    missing_source_barcode: List[str] = []
    missing_destination_barcode: List[str] = []
    clashing_barcodes: List[str] = []  # (source_id, source_barcode)
    file_rows: List[List[str]] = []
    destination_barcodes: List[str] = make_dest_barcode_list(
        destination_artifacts=destination_artifacts
    )

    for destination_artifact in destination_artifacts:
        validate_set_barcode(
            artifact=destination_artifact,
            error_list=missing_destination_barcode,
        )
        source_artifacts = destination_artifact.input_artifact_list()
        buffer = True
        for source_artifact in source_artifacts:
            validate_set_barcode(artifact=source_artifact, error_list=missing_source_barcode)
            validate_unique_barcodes(
                source_artifact=source_artifact,
                destination_barcodes=destination_barcodes,
                clashing_barcodes=clashing_barcodes,
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
                missing_file_udfs.append(source_artifact.samples[0].id)
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

    all_err_msgs: str = ""
    if missing_file_udfs:
        all_err_msgs += f"The following samples are missing UDFs and were not added to the file: {', '.join(missing_file_udfs)}. "
    if missing_source_barcode:
        all_err_msgs += f"The following samples are missing the source barcode: {', '.join(missing_source_barcode)}. "
    if missing_destination_barcode:
        all_err_msgs += f"The following samples are missing the destination barcode: {', '.join(missing_destination_barcode)}. "
    if clashing_barcodes:
        unique_clashing_barcodes: set = set(clashing_barcodes)
        all_err_msgs += (
            f"The following destination container barcodes clash with the input container barcodes. "
            f"Please make sure the destination barcodes are unique! {', '.join(unique_clashing_barcodes)}."
        )
    if all_err_msgs:
        raise MissingUDFsError(f"Error creating the normalization file. " f"{(all_err_msgs)}")


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
    """Script to make a Hamilton normalization file."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process: Process = ctx.obj["process"]
    artifacts: List[Artifact] = get_artifacts(process=process, measurement=measurement)
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
