import csv
import sys
from pathlib import Path
from typing import List

import click
import logging
from genologics.lims import Lims

from cg_lims import options
from cg_lims.EPPs.files.csv_for_kapa_truble_shooting.models import DebugKapaCSV, HEADERS
from cg_lims.models.api.master_steps import (
    HybridizeLibraryTWIST,
    AliquotsamplesforenzymaticfragmentationTWIST,
    KAPALibraryPreparation,
    PoolsamplesforhybridizationTWIST,
    CaptureandWashTWIST,
    BeadPurificationTWIST,
    BufferExchange,
)
from cg_lims.exceptions import LimsError, FileError
from cg_lims.get.artifacts import get_artifact_by_name
from cg_lims.get.files import get_file_path

LOG = logging.getLogger(__name__)


def file_has_comma(file: Path) -> bool:
    """Checking for , in file."""
    with open(file, "r") as file_content:
        content_as_string = str(file_content.read())
        return "," in content_as_string


def build_sample_row(lims: Lims, sample_id: str) -> list:
    sample_row = DebugKapaCSV(SampleID=sample_id)
    sample_row.set_hybridize(hybridize=HybridizeLibraryTWIST(lims=lims, sample_id=sample_id))
    sample_row.set_aliquot(
        aliquot=AliquotsamplesforenzymaticfragmentationTWIST(lims=lims, sample_id=sample_id)
    )
    sample_row.set_kapa(kapa=KAPALibraryPreparation(lims=lims, sample_id=sample_id))
    sample_row.set_pool(pool=PoolsamplesforhybridizationTWIST(lims=lims, sample_id=sample_id))
    sample_row.set_capture(capture=CaptureandWashTWIST(lims=lims, sample_id=sample_id))
    sample_row.set_bead(bead=BeadPurificationTWIST(lims=lims, sample_id=sample_id))
    sample_row.set_buffer(buffer=BufferExchange(lims=lims, sample_id=sample_id))

    sample_row_dict = sample_row.dict(by_alias=True)
    return [sample_row_dict.get(header) for header in HEADERS]


@click.command()
@options.samples_file(help="Txt file with sample ids. (One per row!)")
@options.file_placeholder(help="File placeholder name.")
@options.local_file()
@click.pass_context
def trouble_shoot_kapa(ctx, samples_file: str, file: str, local_file: str):
    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    lims = ctx.obj["lims"]
    process = ctx.obj["process"]
    if local_file:
        file_path_str = local_file
    else:
        file_art = get_artifact_by_name(process=process, name=samples_file)
        file_path_str = get_file_path(file_art)

    file_path = Path(file_path_str)

    try:
        if not file_path.exists():
            LOG.error("File not existing")
            raise FileError(message="File not existing")

        if file_has_comma(file=file_path):
            LOG.error("File wrong format.")
            raise FileError(message="File wrong format.")

        with open(file_path_str, "r") as samples:
            sample_list = [sample_id.strip("\n") for sample_id in samples.readlines()]

        with open(f"{file}_kapa_debug.csv", "w", newline="\n") as new_csv:
            wr = csv.writer(new_csv, delimiter=",")
            wr.writerow(HEADERS)
            sample_rows: List[List[str]] = [
                build_sample_row(lims, sample_id) for sample_id in sample_list
            ]
            wr.writerows(sample_rows)
        click.echo("Twist csv file has been generated.")
    except LimsError as e:
        LOG.info(e.message)
        sys.exit(e.message)
