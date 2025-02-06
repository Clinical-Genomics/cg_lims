import logging
import sys
from typing import Dict, List, Optional

import click
from cg_lims.clients.smrt_link.models import SmrtLinkConfig
from cg_lims.clients.smrt_link.smrt_link_client import SmrtLinkClient
from cg_lims.exceptions import InvalidValueError, LimsError
from genologics.entities import Process

LOG = logging.getLogger(__name__)


SMRT_LINK_RUN_KEYS: Dict[str, str] = {
    "Run ID": "context",
    "Run Name": "name",
    "Instrument Name": "instrumentName",
    "Instrument Serial Number": "instrumentSerialNumber",
    "Instrument Type": "instrumentType",
    "Chip Type": "chipType",
    "Plate 1 ID": "plate1",
    "Plate 2 ID": "plate2",
    "Chemistry Version": "chemistrySwVersion",
    "Started At": "startedAt",
    "Completed At": "completedAt",
    "Total Cells in Run": "totalCells",
}


def get_run_name(process: Process) -> str:
    """Get the Run Name UDF value from a step."""
    setup_steps: List[Process] = process.parent_processes()
    if len(set(setup_steps)) > 1:
        raise InvalidValueError(
            "There's too many parent processes for the given step! "
            "All samples in the step needs to be from the same run."
        )
    return setup_steps[0].udf.get("Run Name")


def get_smrt_link_run(client: SmrtLinkClient, run_name: str) -> Dict:
    """Return a SMRT Link run dict object given a specific run name."""
    runs: List[Dict] = client.get_runs(name=run_name)
    if len(runs) > 1:
        raise InvalidValueError(
            f"Found {len(runs)} matching runs in SMRT Link named '{run_name}'. Can't determine which one to use!"
        )
    elif not runs:
        raise InvalidValueError(
            f"Could not find any runs in SMRT Link named '{run_name}'! "
            f"Please double check that the run name in the previous step is correct."
        )
    return runs[0]


def get_value_from_dict(run_dict: Dict, key: str) -> Optional[str]:
    """Return a value from a run dict given a particular key. A None object is returned if no matching key is found."""
    try:
        value: Optional[str] = run_dict[key]
    except KeyError:
        LOG.info(f"No value found for '{key}' in the run. Skipping.")
        value = None
    return value


def create_run_link(run_dict: Dict, client: SmrtLinkClient) -> str:
    """Create and return a link to the SMRT Link page of a sequencing run."""
    uuid: str = get_value_from_dict(run_dict=run_dict, key="uniqueId")
    return f"{client.base_url}/sl/runs/{uuid}"


def set_run_udfs(client: SmrtLinkClient, process: Process) -> None:
    """Set the process UDFs of a Revio Run step."""
    run_name: str = get_run_name(process=process)
    run_dict: Dict = get_smrt_link_run(client=client, run_name=run_name)

    for udf_name, json_field in SMRT_LINK_RUN_KEYS.items():
        process.udf[udf_name] = get_value_from_dict(run_dict=run_dict, key=json_field)

    process.udf["SMRT Link Run"] = create_run_link(run_dict=run_dict, client=client)
    process.put()


@click.command()
@click.pass_context
def fetch_smrtlink_run_information(ctx):
    """Fetches run information from the SMRT Link API"""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process: Process = ctx.obj["process"]
    smrt_link_config: SmrtLinkConfig = ctx.obj["smrt_link"]
    smrt_link_client: SmrtLinkClient = smrt_link_config.client()

    try:
        set_run_udfs(client=smrt_link_client, process=process)
        message: str = "Run information has been successfully fetched from SMRT Link!"
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
