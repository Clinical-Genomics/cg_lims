import logging
import click
from typing import List, Optional
from genologics.lims import Lims
from genologics.entities import Sample
import datetime

from cg_lims import options

LOG = logging.getLogger(__name__)

FILE_HEADER: str = "Sample ID,Application Tag,Source type,Tumor,Received at,Status"
APP_TAGS: List[str] = ["EX", "PA"]


def get_status(sample: Sample) -> str:
    """Get the current status of a given sample."""
    cancelled_status: Optional[str] = sample.udf.get("cancelled")
    if cancelled_status and cancelled_status.lower() == "yes":
        return "Cancelled"
    elif sample.udf.get("Delivered at") is not None:
        return f"Delivered {sample.udf.get('Delivered at')}"
    else:
        return "Not delivered"


def get_file_row(sample: Sample) -> str:
    """Return the result file .csv row of a sample."""
    return (
        f"{sample.id},"
        f"{sample.udf.get('Sequencing Analysis')},"
        f"{sample.udf.get('Source')},"
        f"{sample.udf.get('tumor')},"
        f"{sample.udf.get('Received at')},"
        f"{get_status(sample)}"
    )


def convert_to_datetime(date_string: str) -> datetime:
    """Return a datetime object from date string structured as YEAR-MONTH-DAY"""
    date: List[str] = date_string.split("-")
    return datetime.date(int(date[0]), int(date[1]), int(date[2]))


@click.command()
@options.file_placeholder(help="File name.")
@click.option(
    "--from-date",
    required=True,
    help="Earliest date to fetch data from.",
)
@click.option(
    "--to-date",
    required=True,
    help="Latest date to fetch data from.",
)
@click.pass_context
def fetch_tga_samples(ctx, file: str, from_date: str, to_date: str):
    """Fetch all samples received at Clinical Genomics between two given dates.
    Results are then presented in a CSV-file."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    lims: Lims = ctx.obj["lims"]

    samples: List[Sample] = lims.get_samples()
    found_samples: int = 0
    from_date: datetime = convert_to_datetime(date_string=from_date)
    to_date: datetime = convert_to_datetime(date_string=to_date)
    with open(file, "w") as file:
        file.write(FILE_HEADER + "\n")
        for sample in samples:
            if not sample.date_received:
                continue
            if not from_date <= convert_to_datetime(date_string=sample.date_received) <= to_date:
                continue
            for app_tag in APP_TAGS:
                if app_tag in sample.udf.get("Sequencing Analysis"):
                    file_row: str = get_file_row(sample)
                    file.write(file_row + "\n")
                    found_samples += 1

    click.echo(f"File created!\nNumber of samples in file: {found_samples}")
    LOG.info(f"File created!\nNumber of samples in file: {found_samples}")
