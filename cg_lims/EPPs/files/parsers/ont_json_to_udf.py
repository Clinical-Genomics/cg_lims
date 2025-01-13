import glob
import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Dict, List

import click
from cg_lims import options
from cg_lims.exceptions import LimsError, MissingFileError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts
from genologics.entities import Artifact, Process

LOG = logging.getLogger(__name__)


def get_flow_cell_id(artifact: Artifact) -> str:
    """Return the flow cell ID of an artifact from the connected container's name."""
    container_name: str = artifact.container.name
    if not container_name:
        raise MissingUDFsError(f"Artifact {artifact.name} is missing a flow cell ID!")
    return container_name


def get_experiment_id(artifact: Artifact) -> str:
    """Return the experiment ID of an artifact from the UDF 'ONT Experiment Name'."""
    if not artifact.udf.get("ONT Experiment Name"):
        raise MissingUDFsError(f"Artifact {artifact.name} is missing an experiment ID!")
    return artifact.udf.get("ONT Experiment Name")


def get_report_html_path(artifact: Artifact, root_path: str) -> str:
    """Return the expected file path of the HTML report for a given flow cell artifact."""
    flow_cell_id: str = get_flow_cell_id(artifact=artifact)
    experiment_id: str = get_experiment_id(artifact=artifact)
    sample_id: str = artifact.samples[0].id
    file_path: str = max(
        glob.glob(
            f"{root_path}/{experiment_id}/{sample_id}/*{flow_cell_id}*/report_{flow_cell_id}*.html"
        ),
        key=os.path.getctime,
    )
    if not Path(file_path).is_file():
        message: str = f"No such file: {file_path}"
        LOG.error(message)
        raise MissingFileError(message)
    return file_path


def parse_html(file_path: str) -> Dict:
    """Return report data JSON from an HTML file."""
    with open(file_path) as f:
        data = f.read()
        match = re.findall("const reportData={.*}$", data, re.M)[0]
    json_string = match.split("=")[1]
    return json.loads(json_string)


def get_n50(json_dict: Dict) -> int:
    """Return the N50 value found in the given report data."""
    try:
        return int(json_dict["estimated_n50"])
    except KeyError:
        return 0


def get_estimated_bases(json_dict: Dict) -> int:
    """Return the Estimated Bases value found in the given report data."""
    try:
        return int(json_dict["data_output"]["estimated_bases"])
    except KeyError:
        return 0


def get_passed_bases(json_dict: Dict) -> int:
    """Return the Passed Bases value found in the given report data."""
    try:
        return int(json_dict["basecalling"]["bases_called_pass"])
    except KeyError:
        return 0


def get_failed_bases(json_dict: Dict) -> int:
    """Return the Failed Bases value found in the given report data."""
    try:
        return int(json_dict["basecalling"]["bases_called_fail"])
    except KeyError:
        return 0


def get_read_count(json_dict: Dict) -> int:
    """Return the read count found in the given report data."""
    try:
        return int(json_dict["data_output"]["reads_generated"])
    except KeyError:
        return 0


def set_sequencing_qc(artifact: Artifact, json_dict: Dict) -> None:
    """Set sequencing QC metrics to the matching artifact UDFs."""
    artifact.udf["Reads Generated"] = get_read_count(json_dict=json_dict)
    artifact.udf["Estimated Bases"] = get_estimated_bases(json_dict=json_dict)
    artifact.udf["QC Passed Bases"] = get_passed_bases(json_dict=json_dict)
    artifact.udf["QC Failed Bases"] = get_failed_bases(json_dict=json_dict)
    artifact.udf["Estimated N50"] = get_n50(json_dict=json_dict)
    artifact.put()


@click.command()
@options.root_path()
@click.pass_context
def parse_ont_report(ctx, root_path: str):
    """Script to parse sequencing metrics from ONT report JSONs and set artifact UDFs."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process: Process = ctx.obj["process"]

    try:
        artifacts: List[Artifact] = get_artifacts(process=process, input=True)

        for artifact in artifacts:
            file_path: str = get_report_html_path(artifact=artifact, root_path=root_path)
            json_dict: Dict = parse_html(file_path=file_path)
            set_sequencing_qc(artifact=artifact, json_dict=json_dict)

        click.echo("Sequencing metrics were successfully read!")
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
