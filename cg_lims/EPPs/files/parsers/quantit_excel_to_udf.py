import logging
import sys
from pathlib import Path
from typing import Dict

import click
import pandas as pd
from cg_lims import options
from cg_lims.exceptions import LimsError, MissingArtifactError, MissingFileError
from cg_lims.get.artifacts import create_well_dict, get_artifact_by_name
from cg_lims.get.files import get_file_path
from genologics.entities import Artifact, Process

LOG = logging.getLogger(__name__)


def set_udfs(udf: str, well_dict: dict, result_file: Path):
    """Reads the Quant-iT Excel file and sets the value for each sample"""

    failed_artifacts: int = 0
    skipped_artifacts: int = 0
    df: pd.DataFrame = pd.read_excel(result_file, skiprows=11, header=None)
    for index, row in df.iterrows():
        if row[0] not in well_dict.keys():
            LOG.info(f"Well {row[0]} is not used by a sample in the step, skipping.")
            skipped_artifacts += 1
            continue
        elif pd.isna(row[2]):
            LOG.info(
                f"Well {row[0]} does not have a valid concentration value ({row[2]}), skipping."
            )
            failed_artifacts += 1
            continue
        artifact: Artifact = well_dict[row[0]]
        artifact.udf[udf] = row[2]
        artifact.put()

    if failed_artifacts or skipped_artifacts:
        error_message: str = "Warning:"
        if failed_artifacts:
            error_message += f" Skipped {failed_artifacts} artifact(s) with wrong and/or blank values for some UDFs."
        if skipped_artifacts:
            error_message += f" Skipped {failed_artifacts} artifact(s) as they weren't represented in the result file."
        raise MissingArtifactError(error_message)


@click.command()
@options.file_placeholder(help="File placeholder name.")
@options.local_file()
@options.udf()
@options.input()
@click.pass_context
def quantit_excel_to_udf(
    ctx,
    file: str,
    local_file: str,
    udf: str,
    input: bool,
):
    """Script to copy data from a Quant-iT result Excel file to concentration UDFs based on well position"""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process: Process = ctx.obj["process"]

    if local_file:
        file_path: str = local_file
    else:
        file_art: Artifact = get_artifact_by_name(process=process, name=file)
        file_path: str = get_file_path(file_art)

    try:
        if not Path(file_path).is_file():
            raise MissingFileError(f"No such file: {file_path}")
        well_dict: Dict[str, Artifact] = create_well_dict(
            process=process, input_flag=input, quantit_well_format=True
        )
        set_udfs(udf=udf, well_dict=well_dict, result_file=Path(file_path))
        click.echo(f"Updated {len(well_dict.keys())} artifact(s) successfully.")
    except LimsError as e:
        sys.exit(e.message)
