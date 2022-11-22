import click
import csv
import logging
from genologics.lims import Lims
from genologics.entities import Sample

from cg_lims.exceptions import LimsError
from cg_lims.get.artifacts import get_sample_artifact
from typing import List

LOG = logging.getLogger(__name__)


def check_cancelled_status(sample: Sample) -> bool:
    status = sample.udf.get("cancelled")
    if status is None or status.lower() != "yes":
        return False
    else:
        return True


def get_samples_from_source(source_types: List[str], skip_cancelled: bool, lims: Lims) -> List[Sample]:
    samples_from_sources = []
    for source in source_types:
        udf_dict = {"Source": source}
        found_samples = lims.get_samples(udf=udf_dict)
        cancelled_samples = 0
        for sample in found_samples:
            if skip_cancelled and check_cancelled_status(sample=sample):
                cancelled_samples += 1
                message = f"Skipping cancelled sample {sample.id}."
                LOG.info(message)
                continue
            samples_from_sources.append(sample)
        message = f"Found {len(found_samples)} sample(s) of source type '{source}'."
        if skip_cancelled:
            message = message + f" Skipped {cancelled_samples} of them because of cancellation status."
        LOG.info(message)
        click.echo(message)
    return samples_from_sources


def print_fetched_samples(
        samples: List[Sample],
        udf_name: str,
        max_amount: str,
        min_amount: str,
        file_path: str,
        lims: Lims,
) -> None:

    sample_rows = []
    missing_udf = 0
    outside_threshold = 0
    for sample in samples:
        sample_artifact = get_sample_artifact(lims=lims, sample=sample)
        if not udf_name:
            sample_rows.append([sample.id, sample.udf.get("Source")])
            continue
        udf_value = sample_artifact.udf.get(udf_name)
        if not udf_value:
            missing_udf += 1
            continue
        if min_amount and float(udf_value) < float(min_amount):
            outside_threshold += 1
            continue
        if max_amount and float(udf_value) > float(max_amount):
            outside_threshold += 1
            continue
        sample_rows.append([sample.id, udf_value, sample.udf.get("Source")])

    if not udf_name:
        headers = ["Sample ID", "Source"]
    else:
        headers = ["Sample ID", udf_name, "Source"]
        if outside_threshold > 0 or missing_udf > 0:
            message = f"Removed a total of {outside_threshold} sample(s) that did not fulfill threshold requirements" \
                      f" and {missing_udf} because of missing UDF values."
            LOG.info(message)
            click.echo(message)
    with open(f"{file_path}.csv", "w", newline="\n") as new_csv:
        wr = csv.writer(new_csv, delimiter=",")
        wr.writerow(headers)
        wr.writerows(sample_rows)


@click.command()
@click.option(
    "--source-type",
    "-s",
    required=False,
    multiple=True,
    help="What source type should be fetched. Allows multiple different sources.",
)
@click.option(
    "--max-udf-amount",
    "-mx",
    required=False,
    help="Don't fetch samples OVER a certain UDF value.",
)
@click.option(
    "--min-udf-amount",
    "-mn",
    required=False,
    help="Don't fetch samples BELOW a certain UDF value.",
)
@click.option(
    "--udf-name",
    "-u",
    required=False,
    help="Fetch samples depending on a specific UDF value. "
         "Use in conjecture with max and/or min value options. "
         "At the moment only works on Sample Artifact UDFs.",
)
@click.option(
    "--file-name",
    "-f",
    required=True,
    help="Prefix of output sample csv-file.",
)
@click.option(
    "--skip-cancelled",
    required=False,
    is_flag=True,
    help="Flag to skip samples which have been cancelled in LIMS.",
)
@click.pass_context
def fetch_sample_info(
        ctx,
        source_type: List[str],
        max_udf_amount: str,
        min_udf_amount: str,
        udf_name: str,
        file_name: str,
        skip_cancelled: bool = False,
):
    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    lims = ctx.obj["lims"]

    try:
        samples_from_sources = get_samples_from_source(
            source_types=source_type,
            skip_cancelled=skip_cancelled,
            lims=lims,
        )
        print_fetched_samples(
            samples=samples_from_sources,
            udf_name=udf_name,
            max_amount=max_udf_amount,
            min_amount=min_udf_amount,
            file_path=file_name,
            lims=lims,
        )
        message = f"Sample info file has been created."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        click.echo(e.message)
