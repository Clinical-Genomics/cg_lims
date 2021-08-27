#!/usr/bin/env python
import logging
import sys
from pathlib import Path
from typing import List

import click
from genologics.lims import Artifact

from cg_lims import options
from cg_lims.EPPs.files.hamilton.models import CovidPrepFileRow
from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.files.manage_csv_files import build_csv, sort_csv
from cg_lims.get.artifacts import get_artifacts
from cg_lims.get.fields import get_index_well, get_artifact_well

LOG = logging.getLogger(__name__)

HEADERS = ["LIMS ID", "Sample Well", "Destination Well", "Index Well"]


def get_file_data_and_write(destination_artifacts: List[Artifact], file: str, pool: bool):
    """Making a sars cov 2 prep file for hamilton."""

    failed_samples = []
    file_rows = []
    for destination_artifact in destination_artifacts:
        source_artifacts: List[Artifact] = destination_artifact.input_artifact_list()
        for source_artifact in source_artifacts:
            try:
                row_data = CovidPrepFileRow(
                    lims_id=source_artifact.samples[0].id,
                    sample_well=get_artifact_well(source_artifact),
                    destination_well=get_artifact_well(destination_artifact),
                    index_well="-" if pool else get_index_well(artifact=destination_artifact),
                )
            except:
                failed_samples.append(source_artifact.id)
                continue

            row_data_dict = row_data.dict(by_alias=True)
            file_rows.append([row_data_dict[header] for header in HEADERS])

    build_csv(file=Path(file), rows=file_rows, headers=HEADERS)
    sort_csv(
        file=Path(file),
        columns=["Sample Well"],
        well_columns=["Sample Well"],
    )

    if failed_samples:
        raise MissingUDFsError(
            f"All samples were not added to the file. Udfs missing for samples: {', '.join(failed_samples)}"
        )


@click.command()
@options.file_placeholder(help="Hamilton Noramlization File")
@options.file_suffix()
@options.pooling_step()
@click.pass_context
def sars_cov2_prep_file(ctx: click.Context, file: str, pooling_step: bool, suffix: str):
    """Script to make a hamilton normalization file"""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process = ctx.obj["process"]
    artifacts = get_artifacts(process=process, input=False)
    container_name = artifacts[0].location[0].name
    try:
        get_file_data_and_write(
            pool=pooling_step,
            destination_artifacts=artifacts,
            file=f"{file}-{suffix}-{container_name}.txt",
        )
        click.echo("The file was successfully generated.")
    except LimsError as e:
        sys.exit(e.message)
