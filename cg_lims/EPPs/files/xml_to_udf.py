import glob
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List
from xml.etree import ElementTree

import click
from cg_lims import options
from cg_lims.exceptions import LimsError, MissingFileError
from genologics.entities import Process
from genologics.lims import Lims

LOG = logging.getLogger(__name__)

RUN_PARAMETERS_KEYS: Dict[str, str] = {"RunId": "Run ID", "OutputFolder": "Output Folder"}

CONSUMABLE_KEYS = {
    "FlowCell": {
        "SerialNumber": "Flow Cell ID",
        "LotNumber": "Flow Cell Lot Number",
        "PartNumber": "Flow Cell Part Number",
        "ExpirationDate": "Flow Cell Expiration Date",
        "Mode": "Flow Cell Mode",
    },
    "Reagent": {
        "SerialNumber": "Reagent Serial Number",
        "LotNumber": "Reagent Lot Number",
        "PartNumber": "Reagent Part Number",
        "ExpirationDate": "Reagent Expiration Date",
    },
    "Buffer": {
        "SerialNumber": "Buffer Serial Number",
        "LotNumber": "Buffer Lot Number",
        "PartNumber": "Buffer Part Number",
        "ExpirationDate": "Buffer Expiration Date",
    },
    "SampleTube": {
        "SerialNumber": "Sample Tube Serial Number",
        "LotNumber": "Sample Tube Lot Number",
        "PartNumber": "Sample Tube Part Number",
        "ExpirationDate": "Sample Tube Expiration Date",
    },
    "Lyo": {
        "SerialNumber": "Lyo Serial Number",
        "LotNumber": "Lyo Lot Number",
        "PartNumber": "Lyo Part Number",
        "ExpirationDate": "Lyo Expiration Date",
    },
}


def get_flow_cell_id(process: Process) -> str:
    """Return flow cell ID from container name."""
    return process.parent_processes()[0].output_containers()[0].name


def get_run_info(process: Process) -> str:
    """Return RunInfo-file from location on the server."""
    flow_cell_id: str = get_flow_cell_id(process=process)
    return max(
        glob.glob(f"/home/gls/hiseq_data/flow_cell_preproc/*{flow_cell_id}/RunInfo.xml"),
        key=os.path.getctime,
    )


def get_run_parameters(process: Process) -> str:
    """Return RunParameters-file from location on the server."""
    flow_cell_id: str = get_flow_cell_id(process=process)
    return max(
        glob.glob(f"/home/gls/hiseq_data/flow_cell_preproc/*{flow_cell_id}/RunParameters.xml"),
        key=os.path.getctime,
    )


def attach_result_files(process: Process, lims: Lims) -> None:
    """Attach sequencing result files to process in LIMS."""
    for outart in process.all_outputs():
        if outart.type == "ResultFile" and outart.name == "Run Info":
            try:
                lims.upload_new_file(outart, get_run_info(process=process))
            except:
                raise (RuntimeError("No RunInfo.xml Found!"))
        elif outart.type == "ResultFile" and outart.name == "Run Parameters":
            try:
                lims.upload_new_file(outart, get_run_parameters(process=process))
            except:
                raise (RuntimeError("No RunParameters.xml Found!"))


def parse_xml_file(file_path: Path) -> ElementTree:
    """Return ElementTree object of given XML file."""
    return ElementTree.parse(file_path).getroot()


def set_process_udfs(xml: ElementTree, process: Process) -> None:
    """Set process UDFs from parameters found in given XML data."""
    for parameter_name, udf_name in RUN_PARAMETERS_KEYS.items():
        process.udf[udf_name] = xml.find(parameter_name).text

    consumable_block: ElementTree = xml.find("ConsumableInfo")
    consumables: List[ElementTree] = consumable_block.findall("ConsumableInfo")

    for consumable in consumables:
        consumable_type: str = consumable.find("Type").text
        if consumable.find("Type").text not in CONSUMABLE_KEYS.keys():
            continue
        for parameter_name, udf_name in CONSUMABLE_KEYS[consumable_type].items():
            process.udf[udf_name] = consumable.find(parameter_name).text

    process.put()


@click.command()
@options.local_file()
@click.pass_context
def parse_run_parameters(ctx, local_file: str):
    """Script to copy data from RunParameters.xml file to process UDFs."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process = ctx.obj["process"]
    lims = ctx.obj["lims"]

    attach_result_files(process=process, lims=lims)

    if local_file:
        file_path: str = local_file
    else:
        file_path: str = get_run_parameters(process=process)

    try:
        if not Path(file_path).is_file():
            message = f"No such file: {file_path}"
            LOG.error(message)
            raise MissingFileError(message)
        xml: ElementTree = parse_xml_file(file_path=Path(file_path))
        set_process_udfs(xml=xml, process=process)
        click.echo("The UDFs were successfully set.")
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
