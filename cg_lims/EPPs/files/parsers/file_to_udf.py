import csv
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import click
from cg_lims import options
from cg_lims.exceptions import ArgumentError, LimsError, MissingArtifactError, MissingFileError
from cg_lims.get.artifacts import create_well_dict, get_artifact_by_name
from cg_lims.get.files import get_file_path
from genologics.entities import Artifact, Process

LOG = logging.getLogger(__name__)


def make_parameter_dict(
    udfs: Tuple[str], value_fields: Tuple[str], files: List[str], well_fields: Tuple[str]
) -> Dict[str, Dict[str, Dict[str, str]]]:
    """
    Create a dictionary mapping file names to their corresponding well names and UDF (User Defined Field) values.

    Args:
        udfs (Tuple[str]): A tuple of UDF names.
        value_fields (Tuple[str]): A tuple of value field names corresponding to the UDFs.
        files (List[str]): A list of file names.
        well_fields (Tuple[str]): A tuple of well names.

    Returns:
        Dict[str, Dict[str, Dict[str, str]]]: A dictionary with the structure:
            {
                <File>: {
                    'Well Name': <Well Name>,
                    'UDF': {
                        <UDF 1>: <Field 1>,
                        <UDF 2>: <Field 2>,
                        ...
                    }
                }
            }

    Raises:
        ArgumentError: If the lengths of `udfs`, `value_fields`, `files`, and `well_fields` are not equal.
    """
    if not (len(udfs) == len(value_fields) == len(files) == len(well_fields)):
        raise ArgumentError(
            f"The number of UDFs to update, value fields, well names and input files must all be equal."
        )
    param_dict: Dict[str, Dict[str, Dict[str, str]]] = {}
    for i in range(len(files)):
        if files[i] not in param_dict:
            param_dict[files[i]] = {"Well Name": well_fields[i], "UDF": {}}
        param_dict[files[i]]["UDF"][udfs[i]] = value_fields[i]
    return param_dict


def get_file_placeholder_paths(placeholder_names: List[str], process: Process) -> List[str]:
    """Convert a list of file placeholder names to complete file paths."""
    file_paths: List[str] = []
    for placeholder_name in placeholder_names:
        file_artifact: Artifact = get_artifact_by_name(process=process, name=placeholder_name)
        file_paths.append(get_file_path(file_artifact=file_artifact))
    return file_paths


def set_udfs_from_file(
    well_field: str, udf_vf_dict: Dict[str, str], well_dict: Dict[str, Artifact], result_file: Path
) -> List[str]:
    """Parse a CSV file and set the corresponding UDF values for each sample."""
    error_msg: List[str] = []
    passed_arts: int = 0
    with open(result_file, newline="", encoding="latin1") as csvfile:
        reader: csv.DictReader = csv.DictReader(csvfile)
        for sample in reader:
            well: str = sample.get(well_field)
            if well not in well_dict:
                LOG.info(f"Well {well} was not found in the step. Skipping!")
                continue
            artifact: Artifact = well_dict[well]
            for udf_name in list(udf_vf_dict.keys()):
                if udf_vf_dict[udf_name] not in reader.fieldnames:
                    LOG.info(
                        f"Value {udf_vf_dict[udf_name]} does not exist in file {result_file}, skipping."
                    )
                    continue
                value_field: str = udf_vf_dict[udf_name]
                value: Any = sample.get(value_field)
                if not value:
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
    param_dict: Dict[str, Dict[str, Dict[str, str]]],
    well_dict: dict,
) -> None:
    """Loop through each given file and parse out the given values which are then set to their corresponding UDFs."""

    error_message: List[str] = []

    for file in param_dict.keys():
        well_field: str = param_dict[file]["Well Name"]
        if not Path(file).is_file():
            raise MissingFileError(f"No such file: {file}")
        error_message += set_udfs_from_file(
            well_field=well_field,
            udf_vf_dict=param_dict[file]["UDF"],
            well_dict=well_dict,
            result_file=Path(file),
        )

    if error_message:
        error_string: str = " ".join(list(set(error_message)))
        raise MissingArtifactError(error_string + " See the log for details.")


@click.command()
@options.file_placeholders(help="File placeholder name.")
@options.local_files()
@options.udfs()
@options.well_fields()
@options.value_fields()
@options.input()
@click.pass_context
def csv_well_to_udf(
    ctx,
    files: Tuple[str],
    local_files: Tuple[str],
    udfs: Tuple[str],
    well_fields: Tuple[str],
    value_fields: Tuple[str],
    input: bool,
):
    """Script to copy data from files to UDFs based on well position."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process: Process = ctx.obj["process"]

    try:
        if local_files:
            files: List[str] = list(local_files)
        else:
            files: List[str] = get_file_placeholder_paths(
                placeholder_names=list(files), process=process
            )

        well_dict: Dict[str, Artifact] = create_well_dict(process=process, input_flag=input)
        param_dict: Dict[str, Dict[str, Dict[str, str]]] = make_parameter_dict(
            udfs=udfs, value_fields=value_fields, files=files, well_fields=well_fields
        )
        print(param_dict)
        set_udfs(
            param_dict=param_dict,
            well_dict=well_dict,
        )
        click.echo("The UDFs were successfully populated.")
    except LimsError as e:
        sys.exit(e.message)
