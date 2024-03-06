import glob
import json
import logging
import os
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
    """Return flow cell ID from artifact."""
    if not artifact.udf.get("ONT Flow Cell ID"):
        raise MissingUDFsError(f"Artifact {artifact.name} is missing a flow cell ID!")
    return artifact.udf.get("ONT Flow Cell ID")


def get_experiment_id(artifact: Artifact) -> str:
    """"""
    if not artifact.udf.get("ONT Experiment Name"):
        raise MissingUDFsError(f"Artifact {artifact.name} is missing an experiment ID!")
    return artifact.udf.get("ONT Experiment Name")


def get_report_json_path(artifact: Artifact, root_path: str) -> str:
    """"""
    flow_cell_id: str = get_flow_cell_id(artifact=artifact)
    experiment_id: str = get_experiment_id(artifact=artifact)
    sample_id: str = artifact.samples[0].id
    file_path: str = max(
        glob.glob(
            f"{root_path}/{experiment_id}/{sample_id}/*{flow_cell_id}*/report_{flow_cell_id}*.json"
        ),
        key=os.path.getctime,
    )
    if not Path(file_path).is_file():
        message: str = f"No such file: {file_path}"
        LOG.error(message)
        raise MissingFileError(message)
    return file_path


def parse_json(file_path: str) -> Dict:
    """"""
    with open(file_path) as f:
        data = json.load(f)
    return data


def get_n50(json_dict: Dict) -> int:
    """"""
    try:
        return int(
            json_dict["acquisitions"][3]["read_length_histogram"][-2]["plot"]["histogram_data"][0][
                "n50"
            ]
        )
    except KeyError:
        return 0


def get_estimated_bases(json_dict: Dict) -> int:
    """"""
    try:
        return int(
            json_dict["acquisitions"][3]["acquisition_run_info"]["yield_summary"][
                "estimated_selected_bases"
            ]
        )
    except KeyError:
        return 0


def get_passed_bases(json_dict: Dict) -> int:
    """"""
    try:
        return int(
            json_dict["acquisitions"][3]["acquisition_run_info"]["yield_summary"][
                "basecalled_pass_bases"
            ]
        )
    except KeyError:
        return 0


def get_failed_bases(json_dict: Dict) -> int:
    """"""
    try:
        return int(
            json_dict["acquisitions"][3]["acquisition_run_info"]["yield_summary"][
                "basecalled_fail_bases"
            ]
        )
    except KeyError:
        return 0


def get_read_count(json_dict: Dict) -> int:
    """"""
    try:
        return int(
            json_dict["acquisitions"][3]["acquisition_run_info"]["yield_summary"]["read_count"]
        )
    except KeyError:
        return 0


def set_sequencing_qc(artifact: Artifact, json_dict: Dict) -> None:
    """"""
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
    """Script to parse sequencing metrics data from ONT report JSONs and save to artifact UDFs."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process: Process = ctx.obj["process"]

    try:
        artifacts: List[Artifact] = get_artifacts(process=process, input=True)

        for artifact in artifacts:
            file_path: str = get_report_json_path(artifact=artifact, root_path=root_path)
            json_dict: Dict = parse_json(file_path=file_path)
            set_sequencing_qc(artifact=artifact, json_dict=json_dict)

        click.echo("Sequencing metrics were successfully read!")
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
