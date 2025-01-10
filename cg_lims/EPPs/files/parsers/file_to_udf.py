#!/usr/bin/env python

import csv
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import click
from cg_lims import options
from cg_lims.exceptions import ArgumentError, LimsError, MissingArtifactError, MissingFileError
from cg_lims.get.artifacts import create_well_dict, get_artifact_by_name
from cg_lims.get.files import get_file_path
from genologics.entities import Artifact, Process

LOG = logging.getLogger(__name__)


def make_udf_dict(udfs: Tuple[str], value_fields: Tuple[str]) -> Dict[str, str]:
    """"""
    if len(udfs) != len(value_fields):
        raise ArgumentError(
            f"The number of artifact-udfs to update and file value fields must be the same."
        )
    udf_vf_dict: dict = {}
    for i in range(len(udfs)):
        udf_vf_dict[udfs[i]] = value_fields[i]
    return udf_vf_dict


def get_file_placeholder_paths(placeholder_names: List[str], process: Process) -> List[str]:
    """"""
    file_paths = []
    for placeholder_name in placeholder_names:
        file_artifact: Artifact = get_artifact_by_name(process=process, name=placeholder_name)
        file_paths.append(get_file_path(file_artifact=file_artifact))
    return file_paths


def set_udfs_from_file(
    well_field: str, udf_vf_dict: Dict[str, str], well_dict: dict, result_file: Path
) -> List[str]:
    """Reads the csv and sets the value for each sample"""

    error_msg: List[str] = []
    passed_arts: int = 0
    with open(result_file, newline="", encoding="latin1") as csvfile:
        reader: csv.DictReader = csv.DictReader(csvfile)
        for udf_name in list(udf_vf_dict.keys()):
            if udf_vf_dict[udf_name] not in reader.fieldnames:
                LOG.info(
                    f"Value {udf_vf_dict[udf_name]} does not exist in file {result_file}, skipping."
                )
                continue
            value_field: str = udf_vf_dict.pop(udf_name)

            for sample in reader:
                well: str = sample.get(well_field)
                if well not in well_dict:
                    LOG.info(f"Well {well} was not found in the step. Skipping!")
                    continue
                artifact: Artifact = well_dict[well]

                value: Any = sample.get(value_field)
                if value is None:
                    error_msg.append("Some samples in the file had missing values.")
                    LOG.info(f"Missing value for sample {sample} in well {well}. Skipping!")
                    continue
                try:
                    artifact.udf[udf_name] = str(value)
                except:
                    artifact.udf[udf_name] = float(value)
                artifact.put()
                passed_arts += 1

    if passed_arts < len(well_dict.keys()):
        error_msg.append("Some samples in the step were not represented in the file.")

    return error_msg


def set_udfs(
    well_fields: List[str],
    udf_vf_dict: Dict[str, str],
    well_dict: dict,
    file_placeholders: List[str],
    local_files: Optional[List[str]],
    process: Process,
) -> None:
    """"""
    if local_files:
        files: List[str] = local_files
    else:
        files: List[str] = get_file_placeholder_paths(
            placeholder_names=file_placeholders, process=process
        )
    if len(well_fields) != len(files):
        raise ArgumentError(f"The number of files to read  and file value fields must be the same.")

    file_well_list: zip = zip(files, well_fields)
    error_message: List[str] = []

    for file_tuple in file_well_list:
        file: str = file_tuple[0]
        well_field: str = file_tuple[1]
        if not Path(file).is_file():
            raise MissingFileError(f"No such file: {file}")
        error_message += set_udfs_from_file(
            well_field=well_field,
            udf_vf_dict=udf_vf_dict,
            well_dict=well_dict,
            result_file=Path(file),
        )

    if error_message:
        error_string: str = " ".join(list(set(error_message)))
        raise MissingArtifactError(error_string)


@click.command()
@options.file_placeholders(help="File placeholder name.")
@options.local_files()
@options.udf_values()
@options.well_fields()
@options.value_fields()
@options.input()
@click.pass_context
def csv_well_to_udf(
    ctx,
    files: Tuple[str],
    local_files: Tuple[str],
    udf_values: Tuple[str],
    well_fields: Tuple[str],
    value_fields: Tuple[str],
    input: bool,
):
    """Script to copy data from file to udf based on well position"""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process: Process = ctx.obj["process"]

    try:
        well_dict: Dict[str, Artifact] = create_well_dict(process=process, input_flag=input)
        udf_vf_dict: Dict[str, str] = make_udf_dict(udfs=udf_values, value_fields=value_fields)
        set_udfs(
            well_fields=list(well_fields),
            udf_vf_dict=udf_vf_dict,
            well_dict=well_dict,
            file_placeholders=list(files),
            local_files=list(local_files),
            process=process,
        )
        click.echo("The UDFs were successfully populated.")
    except LimsError as e:
        sys.exit(e.message)
