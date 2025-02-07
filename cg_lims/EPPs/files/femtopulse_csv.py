import logging
import sys
from pathlib import Path
from typing import List, Tuple

import click
import pandas as pd
from cg_lims import options
from cg_lims.exceptions import InvalidValueError, LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts
from cg_lims.get.fields import get_artifact_well
from genologics.lims import Artifact, Process

LOG = logging.getLogger(__name__)


def get_sample_artifact_name(artifact: Artifact) -> str:
    """Retrieves the name of the sample associated with the given artifact."""
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
        raise InvalidValueError(f"Number of ladders must be between 1 and 8. Got: {num_of_ladders}")
    return num_of_ladders


def get_data_and_write(artifacts: List[Artifact], num_of_ladders: int, file: str):
    """Make a csv file for a Femtopulse run start with three columns:
    index, sample position and sample name, blank or ladder."""

    # Get well positions and sample names and sort by well position
    samples_and_positions: List[Tuple[str,str]] = [(get_artifact_well(artifact), get_sample_artifact_name(artifact))
        for artifact in artifacts]
    samples_and_positions.sort(key=lambda x: (x[0][0], int(x[0][1:])))

    # Check that no sample is in position 12, where the ladders should be.
    invalid_samples: List[str] = [
        sample for position, sample in samples_and_positions if position.endswith("12")
    ]
    if invalid_samples:
        raise InvalidValueError(
            f"Sample(s) {invalid_samples} in position 12, which is reserved for the ladders."
        )

    # Get all unique rows needed based on sample positions and number of ladders
    all_rows: List = ["A", "B", "C", "D", "E", "F", "G", "H"]
    rows_needed: List = sorted(set(position[0] for position, _ in samples_and_positions))
    for row in all_rows:
        if len(rows_needed) >= num_of_ladders:
            break
        if row not in rows_needed:
            rows_needed.append(row)
    rows_needed.sort()

    # Create a list of positions, sample names, blanks and ladders based on the rows needed for the run.
    sample_position_layout: List = []
    for row in rows_needed:
        row_samples: List[str, str] = [
            (position, sample)
            for position, sample in samples_and_positions
            if position.startswith(row)
        ]
        # Add existing samples for positions 1-11
        for position in range(1, 12):
            well: str = f"{row}{position}"
            sample: str = next((samp for pos, samp in row_samples if pos == well), "")
            sample_position_layout.append((well, sample))
        # Add ladder or empty position for position 12
        ladder: str = "ladder" if rows_needed.index(row) < num_of_ladders else ""
        sample_position_layout.append((f"{row}12", ladder))

    # Create and write dataframe
    df = pd.DataFrame(sample_position_layout, columns=["well positions", "sample names"])
    df.index = range(1, len(df) + 1)
    df.to_csv(Path(file), index=True, header=False, sep=";")

    if len(rows_needed) > num_of_ladders:
        raise InvalidValueError(
            f"Warning: The number of populated sample rows ({len(rows_needed)}) "
            f"exceed the amount of ladders chosen ({num_of_ladders})."
        )

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
    artifacts: List[Artifact] = get_artifacts(process=process, measurement=measurement)

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
