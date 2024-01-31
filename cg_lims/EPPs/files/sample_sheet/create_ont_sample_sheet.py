import logging
import sys
from datetime import date
from pathlib import Path
from typing import List

import click
from cg_lims import options
from cg_lims.EPPs.files.sample_sheet.models import NanoporeSampleSheetHeader
from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.files.manage_csv_files import build_csv
from cg_lims.get.artifacts import get_artifacts
from cg_lims.get.samples import get_one_sample_from_artifact
from genologics.entities import Artifact, Process

LOG = logging.getLogger(__name__)


def get_flow_cell_id(artifact: Artifact) -> str:
    """"""
    if not artifact.udf.get("ONT Flow Cell ID"):
        raise MissingUDFsError(f"Artifact {artifact.name} is missing a flow cell ID!")
    return artifact.udf.get("ONT Flow Cell ID")


def get_flow_cell_type(process: Process) -> str:
    """"""
    if not process.udf.get("ONT Flow Cell Type"):
        raise MissingUDFsError(f"Sample sheet generation requires a flow cell type!")
    return process.udf.get("ONT Flow Cell Type")


def get_sample_id(artifact: Artifact) -> str:
    """"""
    return get_one_sample_from_artifact(artifact=artifact).id


def get_experiment_name(process: Process) -> str:
    """"""
    return f"{date.today()}_{process.id}"


def get_kit(process: Process) -> str:
    """"""
    library_kit = process.udf.get("ONT Prep Kit")
    expansion_kit = process.udf.get("ONT Expansion Kit")
    if not library_kit:
        raise MissingUDFsError("Sample sheet generation requires a library kit name!")
    if expansion_kit:
        library_kit = f"{library_kit} {expansion_kit}"
    return library_kit


def get_header() -> List[str]:
    """"""
    return [
        NanoporeSampleSheetHeader.FLOW_CELL_ID,
        NanoporeSampleSheetHeader.FLOW_CELL_PROD_CODE,
        NanoporeSampleSheetHeader.SAMPLE_ID,
        NanoporeSampleSheetHeader.EXPERIMENT_ID,
        NanoporeSampleSheetHeader.KIT,
    ]


def get_row(artifact: Artifact, process: Process) -> List[str]:
    """"""
    return [
        get_flow_cell_id(artifact=artifact),
        get_flow_cell_type(process=process),
        get_sample_id(artifact=artifact),
        get_experiment_name(process=process),
        get_kit(process=process),
    ]


def get_sample_sheet_content(artifacts: List[Artifact], process: Process) -> List[List[str]]:
    """"""
    rows = []
    for artifact in artifacts:
        rows.append(get_row(artifact=artifact, process=process))
    return rows


@click.command()
@options.file_placeholder(help="File placeholder name.")
@click.pass_context
def create_ont_sample_sheet(ctx, file: str):
    """Create an Oxford Nanopore sample sheet .csv file from an 'ONT Start Sequencing' step."""
    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process = ctx.obj["process"]

    try:
        artifacts: List[Artifact] = get_artifacts(process=process)
        header = get_header()
        sample_sheet_content: List[List[str]] = get_sample_sheet_content(
            artifacts=artifacts, process=process
        )
        file_path = Path(f"{file}_sample_sheet_{get_experiment_name(process=process)}.csv")
        build_csv(rows=sample_sheet_content, headers=header, file=file_path)
        message = "The sample sheet was successfully generated."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
