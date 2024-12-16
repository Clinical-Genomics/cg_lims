import logging
import sys
from pathlib import Path
from typing import List

import click
import pandas as pd
from genologics.lims import Artifact

from cg_lims import options
from cg_lims.exceptions import InvalidValueError, LimsError
from cg_lims.get.artifacts import get_artifacts

LOG = logging.getLogger(__name__)

ROWS = list(range(1,13)) # List numbered 1 to 12
WELL_POSITIONS = [f"A{i}" for i in range(1,13)] # List with well positions A1-A12
SAMPLE_NAMES = [""] * 12 # List with twelve empty positions for sample names


def parse_well(artifact_position: str) -> str:
    """Convert position from format 'A:1' to 'A1'."""
    try:
        row, col = artifact_position.split(":")
        return f"{row}{col}"
    except Exception:
        return None


def get_data_and_write(
        artifacts: List[Artifact],
        file: str
):
    """Make a csv file for a Femtopulse run start with three columns: 
    one numbered 1-12, one with the sample position/well for the run and 
    a column with the sample name or ladder (in the 12th position)."""

    failed_samples: list = []

    for artifact in artifacts:

        artifact_name: str = artifact.samples[0].name
        artifact_well: str = artifact.location[1]

        # Convert sample well format from 'A:1' to 'A1'
        parsed_well: str = parse_well(artifact_well)

        # Checks that the sample well matches with one in the WELL_POSITIONS list and is A1-A11
        if parsed_well in WELL_POSITIONS:
            index: int = WELL_POSITIONS.index(parsed_well)
            if index < 11:
                SAMPLE_NAMES[index] = artifact_name
            else:
                failed_samples.append({"artifact_name": artifact_name, 
                                       "parsed_well": parsed_well, 
                                       "error": "This position is reserved for the ladder"})
        else:
            failed_samples.append({"artifact_name": artifact_name, 
                                "parsed_well": parsed_well, 
                                "error": "Position is not possible for the run"})

    if failed_samples:
        error_message: str = "\n".join(
            f"Sample {sample['artifact_name']} in position {sample['parsed_well']}: {sample['error']}"
        for sample in failed_samples
        )
        raise InvalidValueError(f"Errors found:\n{error_message}")

    # The ladder will always be in well A12
    SAMPLE_NAMES[-1] = "ladder"

    # Create the csv file
    df = pd.DataFrame({
        0: ROWS,
        1: WELL_POSITIONS,
        2: SAMPLE_NAMES
    })
    df.to_csv(Path(file), index=False, header=False)


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
        get_data_and_write(
            artifacts=artifacts,
            file=f"{file}_femtopulse.csv",
        )
        click.echo("The file was successfully generated.")
    except LimsError as e:
        sys.exit(e.message)