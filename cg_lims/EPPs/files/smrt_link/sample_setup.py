import logging
import sys
from pathlib import Path
from typing import List

import click
from cg_lims import options
from cg_lims.EPPs.files.smrt_link.models import SAMPLE_SETUP_CSV_HEADER, SampleSetup
from cg_lims.exceptions import LimsError
from cg_lims.files.manage_csv_files import build_csv
from cg_lims.get.artifacts import get_artifacts
from genologics.entities import Artifact, Process

LOG = logging.getLogger(__name__)


def get_csv_sample_rows(process: Process) -> List[List[str]]:
    """Return the sample rows of the Sample Setup CSV"""
    artifacts: List[Artifact] = get_artifacts(process=process)
    rows: List[List[str]] = []
    for artifact in artifacts:
        sample_setup_object: SampleSetup = SampleSetup(artifact=artifact)
        rows.append(sample_setup_object.get_sample_setup_row())
    return rows


@click.command()
@options.file_placeholder(help="File placeholder name.")
@click.pass_context
def create_smrtlink_sample_setup(ctx, file: str):
    """Create a sample setup .csv file for SMRT Link import."""
    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process: Process = ctx.obj["process"]

    try:
        sample_setup_csv_rows: List[List[str]] = get_csv_sample_rows(process=process)
        file_path: Path = Path(f"{file}.csv")
        build_csv(rows=sample_setup_csv_rows, file=file_path, headers=SAMPLE_SETUP_CSV_HEADER)
        click.echo("The sample setup CSV was successfully generated.")
    except LimsError as e:
        sys.exit(e.message)
