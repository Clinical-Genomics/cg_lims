import logging
import sys
from typing import Dict, List

import click
from cg_lims.clients.cg.models import PacbioSequencingRun
from cg_lims.clients.cg.status_db_api import StatusDBAPI
from cg_lims.exceptions import LimsError, MissingArtifactError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts
from cg_lims.get.fields import get_alternative_artifact_well
from genologics.entities import Artifact, Process

LOG = logging.getLogger(__name__)


def get_run_id(udf_name: str, process: Process) -> str:
    """"""
    try:
        return process.udf[udf_name]
    except KeyError:
        raise MissingUDFsError("Can't find a run ID value for the step!")


def get_plate_number(artifact: Artifact) -> int:
    """"""
    parent_process: Process = artifact.parent_process
    plate_name: str = artifact.container.name
    if parent_process.udf.get("Plate 1") and parent_process.udf.get("Plate 1") == plate_name:
        return 1
    elif parent_process.udf.get("Plate 2") and parent_process.udf.get("Plate 2") == plate_name:
        return 2
    else:
        raise MissingUDFsError(
            f"Can't find a matching plate name in the run set up! "
            f"Expected plate '{plate_name}', see {parent_process.uri}."
        )


def create_artifact_dict(artifacts: List[Artifact]) -> Dict[int, Dict[str, Artifact]]:
    """"""
    artifact_dict: Dict[int, Dict[str, Artifact]] = {1: {}, 2: {}}
    for artifact in artifacts:
        plate_number: int = get_plate_number(artifact=artifact)
        well: str = get_alternative_artifact_well(artifact=artifact)
        artifact_dict[plate_number][well] = artifact
    return artifact_dict


def find_matching_artifact(
    metric: PacbioSequencingRun, artifact_dict: Dict[int, Dict[str, Artifact]]
) -> Artifact:
    """"""
    well: str = metric.well
    plate_number: int = metric.plate
    try:
        return artifact_dict[plate_number][well]
    except KeyError:
        print(metric)
        print(artifact_dict)
        raise MissingArtifactError(
            f"Can't find a matching artifact in the step for plate {plate_number}, well {well}!"
        )


def set_smrt_cell_metrics(
    metrics: List[PacbioSequencingRun], artifact_dict: Dict[int, Dict[str, Artifact]]
) -> None:
    """"""
    for metric in metrics:
        artifact: Artifact = find_matching_artifact(metric=metric, artifact_dict=artifact_dict)
        artifact.udf["SMRT Cell ID"] = metric.internal_id
        artifact.udf["P0 %"] = metric.p0_percent
        artifact.udf["P1 %"] = metric.p1_percent
        artifact.udf["P2 %"] = metric.p2_percent
        artifact.udf["% reads passing Q30"] = metric.percent_reads_passing_q30
        artifact.put()


@click.command()
@click.pass_context
def smrt_cell_metrics(ctx):
    """"""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process: Process = ctx.obj["process"]
    status_db_api: StatusDBAPI = ctx.obj["status_db"]

    try:
        artifacts: List[Artifact] = get_artifacts(process=process, input=True)
        artifact_dict: Dict[int, Dict[str, Artifact]] = create_artifact_dict(artifacts=artifacts)
        run_id: str = get_run_id(udf_name="Run ID", process=process)
        smrt_cell_values: List[PacbioSequencingRun] = (
            status_db_api.get_pacbio_sequencing_run_from_run_id(run_id=run_id)
        )
        set_smrt_cell_metrics(metrics=smrt_cell_values, artifact_dict=artifact_dict)

        click.echo("The UDFs were successfully populated.")
    except LimsError as e:
        sys.exit(e.message)
