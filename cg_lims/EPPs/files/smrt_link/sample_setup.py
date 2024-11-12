import logging
import re
import sys
from typing import Dict, List, Optional

import click
from cg_lims import options
from cg_lims.EPPs.files.smrt_link.models import SampleSetupObject
from cg_lims.exceptions import InvalidValueError, LimsError
from cg_lims.get.artifacts import get_artifact_lane, get_artifacts
from genologics.entities import Artifact, Process, ReagentType, Sample
from genologics.lims import Lims

LOG = logging.getLogger(__name__)

CSV_HEADER = (
    '"Sample Name",'
    '"Comment",'
    '"System Name",'
    '"Binding Kit",'
    '"Plate",'
    '"Well",'
    '"Number of Samples",'
    '"Application",'
    '"Available Starting Sample Volume (uL)",'
    '"Starting Sample Concentration (ng/uL)",'
    '"Insert Size (bp)",'
    '"Control Kit",'
    '"Cleanup Anticipated Yield (%)",'
    '"On Plate Loading Concentration (pM)",'
    '"Cells to Bind (cells)",'
    '"Prepare Entire Sample",'
    '"Sequencing Primer",'
    '"Target Annealing Sample Concentration (nM)",'
    '"Target Annealing Primer Concentration (nM)",'
    '"Target Binding Concentration (nM)",'
    '"Target Polymerase Concentration (X)",'
    '"Binding Time (min)",'
    '"Cleanup Bead Type",'
    '"Cleanup Bead Concentration (X)",'
    '"Minimum Pipetting Volume (uL)",'
    '"Percent of Annealing Reaction To Use In Binding (%)",'
    '"AMPure Diluted Bound Complex Volume (uL)",'
    '"AMPure Diluted Bound Complex Concentration (ng/uL)",'
    '"AMPure Purified Complex Volume (uL)",'
    '"AMPure Purified Complex Concentration (ng/uL)",'
    '"ProNex Diluted Bound Complex Volume (uL)",'
    '"ProNex Diluted Bound Complex Concentration (ng/uL)",'
    '"ProNex Purified Complex Volume (uL)",'
    '"ProNex Purified Complex Concentration (ng/uL)",'
    '"Requested Cells Alternate (cells)",'
    '"Requested OPLC Alternate (pM)"'
)


def build_step_csv(process: Process) -> str:
    """"""
    artifacts = get_artifacts(process=process)
    output_csv = CSV_HEADER
    for artifact in artifacts:
        sample_setup_object = SampleSetupObject(artifact=artifact)
        output_csv = output_csv + "\n" + sample_setup_object.get_sample_setup_row()

    return output_csv


@click.command()
@options.file_placeholder(help="File placeholder name.")
@click.pass_context
def create_smrtlink_sample_setup(ctx, file: str):
    """Create a sample setup .csv file for SMRT Link import."""
    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process = ctx.obj["process"]

    try:
        sample_setup_csv: str = build_step_csv(process=process)
        with open(f"{file}.csv", "w") as file:
            file.write(sample_setup_csv)
        click.echo("The sample setup CSV was successfully generated.")
    except LimsError as e:
        sys.exit(e.message)
