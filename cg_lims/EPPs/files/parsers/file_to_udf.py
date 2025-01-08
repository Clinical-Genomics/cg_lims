#!/usr/bin/env python

import csv
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

import click
from cg_lims import options
from cg_lims.exceptions import LimsError, MissingArtifactError, MissingFileError
from cg_lims.get.artifacts import create_well_dict, get_artifact_by_name
from cg_lims.get.files import get_file_path
from genologics.entities import Artifact, Process

LOG = logging.getLogger(__name__)


def set_udfs(well_field: str, value_field: str, udf: str, well_dict: dict, result_file: Path):
    """Reads the csv and sets the value for each sample"""

    error_msg: List[str] = []
    passed_arts: int = 0
    with open(result_file, newline="", encoding="latin1") as csvfile:
        reader: csv.DictReader = csv.DictReader(csvfile)
        for sample in reader:
            well: str = sample.get(well_field)
            value: Any = sample.get(value_field)
            if value is None:
                error_msg.append("Some samples in the file had missing values.")
                LOG.info(f"Missing value for sample {sample} in well {well}. Skipping!")
                continue
            elif well not in well_dict:
                LOG.info(f"Well {well} was not found in the step. Skipping!")
                continue
            artifact: Artifact = well_dict[well]
            try:
                artifact.udf[udf] = str(value)
            except:
                artifact.udf[udf] = float(value)
            artifact.put()
            passed_arts += 1

    if passed_arts < len(well_dict.keys()):
        error_msg.append("Some samples in the step were not represented in the file.")

    error_string: str = " ".join(list(set(error_msg)))
    if error_msg:
        raise MissingArtifactError(error_string)


@click.command()
@options.file_placeholder(help="File placeholder name.")
@options.local_file()
@options.udf()
@options.well_field()
@options.value_field()
@options.input()
@click.pass_context
def csv_well_to_udf(
    ctx, file: str, well_field: str, value_field: str, udf: str, input: bool, local_file: str
):
    """Script to copy data from file to udf based on well position"""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process: Process = ctx.obj["process"]

    if local_file:
        file_path: str = local_file
    else:
        file_art: Artifact = get_artifact_by_name(process=process, name=file)
        file_path: str = get_file_path(file_art)

    try:
        if not Path(file_path).is_file():
            raise MissingFileError(f"No such file: {file_path}")
        well_dict: Dict[str, Artifact] = create_well_dict(process=process, input_flag=input)
        set_udfs(well_field, value_field, udf, well_dict, Path(file_path))
        click.echo("The udfs were sucessfully populated.")
    except LimsError as e:
        sys.exit(e.message)
