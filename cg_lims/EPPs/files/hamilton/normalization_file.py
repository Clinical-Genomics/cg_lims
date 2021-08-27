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
from cg_lims.files.manage_csv_files import build_csv, sort_csv
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


def get_file_data_and_write(
    destination_artifacts: List[Artifact], file: str, volume_udf: str, buffer_udf: str, pool: bool
):
    """Making a hamilton normalization file with sample and buffer volumes, source and destination barcodes and wells."""

    failed_samples = []
    file_rows = []
    for destination_artifact in destination_artifacts:
        source_artifacts = destination_artifact.input_artifact_list()
        buffer = True
        for source_artifact in source_artifacts:
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
                failed_samples.append(source_artifact.id)
                continue

            row_data_dict = row_data.dict(by_alias=True)

            file_rows.append([row_data_dict[header] for header in HEADERS])

    build_csv(file=Path(file), rows=file_rows, headers=HEADERS)
    sort_csv(
        file=Path(file),
        columns=["Barcode Source Container", "Source Well", "Destination Well"],
        well_columns=["Source Well", "Destination Well"],
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
def barcode_file(
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
