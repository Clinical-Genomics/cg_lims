import logging
import math
import sys
from pathlib import Path
from typing import List

import click
import pandas as pd
from genologics.lims import Artifact, Process

from cg_lims import options
from cg_lims.exceptions import InvalidValueError, LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts
from cg_lims.get.fields import get_artifact_well

LOG = logging.getLogger(__name__)


def get_sample_artifact_name(artifact: Artifact) -> str:
    artifact_name: str = artifact.samples[0].name
    return artifact_name


def get_number_of_ladders(process: Process) -> int:
    """Returning the number of ladders from a process"""
    num_of_ladders: int = process.udf.get("Number of ladders")
    if not num_of_ladders:
        raise MissingUDFsError(
            f"Missing the number of ladders, please specify a number between 1-8."
        )
    if not 1 <= num_of_ladders <= 8:
        raise InvalidValueError(
            f"Number of ladders must be between 1 and 8. Got: {num_of_ladders}"
        )
    return num_of_ladders


def generate_plate_positions(
    num_of_artifacts: int, num_of_ladders: int
) -> pd.DataFrame:
    """Generate all possible plate positions based on number of artifacts and ladders."""

    ROWS: List = ["A", "B", "C", "D", "E", "F", "G", "H"]
    SAMPLES_PER_ROW: int = 11  # Only using positions 1-11

    # Calculate required number of rows for samples
    required_rows: int = math.ceil(num_of_artifacts / SAMPLES_PER_ROW)
    max_rows: int = max(required_rows, num_of_ladders)
    if max_rows > 8:
        raise InvalidValueError(
            f"Too many rows required ({max_rows}). Maximum is 8 rows."
        )

    WELL_POSITIONS: List = []
    SAMPLE_NAMES: List = []

    # Generate positions for samples (1-11 in each required row) and ladder positions (position 12 in sequential rows)
    for row_id in range(max_rows):
        row_letter: str = ROWS[row_id]
        for col in range(1, 12):  # positions 1-11
            WELL_POSITIONS.append(f"{row_letter}{col}")
            SAMPLE_NAMES.append("")
        WELL_POSITIONS.append(f"{row_letter}12")
        SAMPLE_NAMES.append("ladder" if row_id < num_of_ladders else "")

    return pd.DataFrame(
        {"well positions": WELL_POSITIONS, "sample names": SAMPLE_NAMES}
    )


def get_data_and_write(artifacts: List[Artifact], num_of_ladders: int, file: str):
    """Make a csv file for a Femtopulse run start with three columns:
    index, sample position and sample name or ladder."""

    # Generate the plate layout based on number of artifacts and ladders
    DATAFRAME: pd.DataFrame = generate_plate_positions(
        num_of_artifacts=len(artifacts), num_of_ladders=num_of_ladders
    )

    failed_samples: list = []

    for artifact in artifacts:

        artifact_name: str = get_sample_artifact_name(artifact=artifact)
        artifact_well: str = get_artifact_well(artifact=artifact)

        # Check if well position is valid and not a ladder position
        if artifact_well in DATAFRAME["well positions"].values:
            if artifact_well.endswith("12"):
                failed_samples.append(
                    {
                        "artifact_name": artifact_name,
                        "parsed_well": artifact_well,
                        "error": "This position is reserved for the ladder.",
                    }
                )
            else:
                DATAFRAME.loc[
                    DATAFRAME["well positions"] == artifact_well, "sample names"
                ] = artifact_name
        else:
            failed_samples.append(
                {
                    "artifact_name": artifact_name,
                    "parsed_well": artifact_well,
                    "error": "This position is not suitable for the run.",
                }
            )

    # Prints out error messages
    if failed_samples:
        all_errors = ""
        for sample in failed_samples:
            error_message: str = (
                f"Sample {sample['artifact_name']} in position {sample['parsed_well']}: {sample['error']}"
            )
            all_errors = all_errors + " " + error_message
        raise InvalidValueError(f"Errors found: {all_errors}")

    # Create the csv file
    DATAFRAME.index = range(1, len(DATAFRAME) + 1)
    DATAFRAME.to_csv(Path(file), index=True, header=False, sep=";")


@click.command()
@options.file_placeholder()
@options.measurement()
@click.pass_context
def make_femtopulse_csv(
    ctx: click.Context,
    file: str,
    measurement: bool,
):
    """Script to make a csv file for a Femtopulse run"""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process = ctx.obj["process"]
    artifacts = get_artifacts(process=process, measurement=measurement)

    try:
        num_of_ladders: int = get_number_of_ladders(process=process)
        get_data_and_write(
            artifacts=artifacts,
            num_of_ladders=num_of_ladders,
            file=f"{file}_femtopulse.csv",
        )
        click.echo("The file was successfully generated.")
    except LimsError as e:
        sys.exit(e.message)
