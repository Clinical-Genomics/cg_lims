import logging
import sys
from pathlib import Path
from typing import List

import click
import pandas as pd
from cg_lims import options
from cg_lims.exceptions import InvalidValueError, LimsError
from cg_lims.get.artifacts import get_artifacts
from cg_lims.get.fields import get_artifact_well
from genologics.lims import Artifact

LOG = logging.getLogger(__name__)


WELL_POSITIONS = [f"A{i}" for i in range(1, 13)]  # List with well positions A1-A12
SAMPLE_NAMES = [""] * len(WELL_POSITIONS)  # List with twelve empty positions for sample names
DATAFRAME = pd.DataFrame(
    {"well positions": WELL_POSITIONS, "sample names": SAMPLE_NAMES}
)  # Dataframe with well positions and sample names


def get_sample_artifact_name(artifact: Artifact):

    artifact_name: str = artifact.samples[0].name

    return artifact_name


def get_data_and_write(artifacts: List[Artifact], file: str):
    """Make a csv file for a Femtopulse run start with three columns:
    one numbered 1-12, one with the sample position/well for the run and
    a column with the sample name or ladder (in the 12th position)."""

    failed_samples: list = []

    for artifact in artifacts:

        artifact_name: str = get_sample_artifact_name(artifact=artifact)

        # Fetch sample well in format 'A1'
        artifact_well: str = get_artifact_well(artifact=artifact)

        # Checks that the sample well matches with one in the WELL_POSITIONS list (A1-A11)
        # and adds the sample name to the SAMPLE_NAMES list for that position
        if artifact_well in DATAFRAME["well positions"].values:
            if artifact_well == DATAFRAME["well positions"].iloc[-1]:
                failed_samples.append(
                    {
                        "artifact_name": artifact_name,
                        "parsed_well": artifact_well,
                        "error": "This position is reserved for the ladder.",
                    }
                )
            else:
                DATAFRAME.loc[DATAFRAME["well positions"] == artifact_well, "sample names"] = (
                    artifact_name
                )
        else:
            failed_samples.append(
                {
                    "artifact_name": artifact_name,
                    "parsed_well": artifact_well,
                    "error": "This position is not possible for the run.",
                }
            )

    # Prints out error message(s)
    if failed_samples:
        all_errors = ""
        for sample in failed_samples:
            error_message: str = (
                f"Sample {sample['artifact_name']} in position {sample['parsed_well']}: {sample['error']}"
            )
            all_errors = all_errors + " " + error_message
        raise InvalidValueError(f"Errors found: {all_errors}")

    # The ladder will always be in well A12
    DATAFRAME["sample names"].iloc[-1] = "ladder"

    # Create the csv file
    DATAFRAME.index = range(1, len(DATAFRAME) + 1)
    DATAFRAME.to_csv(Path(file), index=True, header=False)


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
