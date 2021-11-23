"""One time script to add Covid meta data to sample"""
import logging
import pathlib
from datetime import date, datetime
from typing import List

import click
import coloredlogs
import pandas as pd
import yaml
from genologics.entities import Sample
from genologics.lims import Lims

from cg_lims import options
from cg_lims.exceptions import LimsError, MissingSampleError

LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR"]
LOG = logging.getLogger(__name__)
LOG_FORMAT = "%(levelname)s:%(message)s"
ONLY_ADD_IF_DATA_IS_MISSING = [
    "Collection Date",
    "Region",
    "Lab Code",
    "Original Lab",
    "Original Lab Address",
    "Region Code",
]


def get_covid_samples(row: pd.Series, lims: Lims) -> List[Sample]:
    """Tries to find a single sample based on the submitted sample name in the meta data file"""
    sample_name = row["Submitted Sample Name"]
    LOG.info("Trying to find submitted sample %s:", sample_name)
    samples = lims.get_samples(name=sample_name)
    if len(samples) == 0:
        message = f"Sample {sample_name} in meta data file not found in LIMS!"
        LOG.warning(message)
        raise MissingSampleError(message)
    LOG.info("Sample(s) found: %s!", ", ".join([sample.id for sample in samples]))
    return samples


def update_sample_udfs(sample: Sample, udfs: pd.Index, row: pd.Series) -> None:
    """Updates the udfs on a sample with data from the meta data file"""
    for udf in udfs:
        if udf == "Collection Date" and not isinstance(row[udf], date):
            collection_date = row[udf]
            converted_collection_date = datetime.strptime(row[udf], "%Y-%m-%d").date()
            LOG.info(
                "Converting Collection Date from string to date format: %s -> %s",
                collection_date,
                converted_collection_date,
            )
            row[udf] = converted_collection_date
        if udf == "Region Code":
            LOG.info("Converting Region Code from int to string format")
            row[udf] = str(row[udf]).zfill(2)
        if not sample.udf.get(udf):
            LOG.info("Creating udf %s on sample %s: %s", udf, sample.id, row[udf])
        if sample.udf.get(udf) and sample.udf[udf] != row[udf]:
            if udf in ONLY_ADD_IF_DATA_IS_MISSING:
                LOG.warning(
                    "udf %s on sample (%s) differs from meta data (%s), sample will NOT be "
                    "updated!",
                    udf,
                    sample.udf[udf],
                    row[udf],
                )
                continue
            else:
                LOG.info(
                    "Updating udf %s on sample %s: %s -> %s",
                    udf,
                    sample.id,
                    sample.udf[udf],
                    row[udf],
                )
        if sample.udf.get(udf) and sample.udf[udf] == row[udf]:
            LOG.info("Meta data already present on sample %s", sample.id)
        sample.udf[udf] = row[udf]


def set_meta_data_on_samples(meta_data: pd.DataFrame, lims: Lims) -> None:
    """Finds a sample based on the submitted sample name and sets the udfs"""
    successful_updates: int = 0
    failed_updates: int = 0
    udfs: pd.Index = meta_data.columns[1:]
    for _, row in meta_data.iterrows():
        try:
            samples: List[Sample] = get_covid_samples(row, lims)
            for sample in samples:
                LOG.info(
                    "Meta data found for sample %s: Collection Date %s, Region %s, Lab Code %s, "
                    "Original Lab %s, Original Lab Address %s, Region Code %s, Data Analysis %s",
                    sample.id,
                    row["Collection Date"],
                    row["Region"],
                    row["Lab Code"],
                    row["Original Lab"],
                    row["Original Lab Address"],
                    row["Region Code"],
                    row["Data Analysis"],
                )
                update_sample_udfs(sample, udfs, row)
                sample.put()
                successful_updates += 1
        except MissingSampleError:
            failed_updates += 1
    if failed_updates:
        raise LimsError(
            f"Meta data successfully updated on {successful_updates} samples! Number of submitted "
            f"samples not updated: {failed_updates}"
        )


@click.command()
@options.config()
@options.log()
@click.option(
    "--data-file",
    "-f",
    type=click.Path(exists=True, dir_okay=False),
    required=True,
    help="path to file with meta data",
)
@click.option(
    "--log-level",
    type=click.Choice(LEVELS),
    default="INFO",
    help="lowest level to log at",
)
@click.pass_context
def set_sample_meta_data(
    context: click.Context, config: str, log: str, data_file: click.Path, log_level: str
):
    """Script to set Covid meta data on sample udf."""
    with open(config) as file:
        config_data = yaml.load(file, Loader=yaml.FullLoader)
    lims = Lims(
        config_data["BASEURI"], config_data["USERNAME"], config_data["PASSWORD"]
    )
    log_path = pathlib.Path(log)
    log_level = getattr(logging, log_level.upper())
    logging.basicConfig(
        filename=str(log_path.absolute()), filemode="w", level=log_level
    )
    LOG.info(f"Running {context.command_path} with params: {context.params}")
    coloredlogs.install(level=log_level, fmt=LOG_FORMAT)
    meta_data: pd.DataFrame = pd.read_csv(data_file, sep=";")
    try:
        set_meta_data_on_samples(meta_data, lims)
        message = f"All samples updated!"
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        click.echo(e.message)


if __name__ == "__main__":
    set_sample_meta_data()
