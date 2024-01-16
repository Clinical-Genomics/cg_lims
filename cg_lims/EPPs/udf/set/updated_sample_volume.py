import logging
import sys
from typing import List, Optional

import click
from cg_lims import options
from cg_lims.exceptions import LimsError, MissingArtifactError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts, get_latest_analyte, get_sample_artifact
from genologics.entities import Artifact
from genologics.lims import Lims

LOG = logging.getLogger(__name__)


def get_new_volume(original_volume: float, subtracted_volume: float, added_volume: float) -> float:
    """Calculate the updated volume of a sample."""
    return float(original_volume) - float(subtracted_volume) + float(added_volume)


def set_updated_sample_volume(
    destination_artifact: Artifact,
    original_volume: float,
    subtracted_volume: float,
    added_volume: float,
) -> None:
    """Set the updated sample volume (Volume (ul)) to an given artifact."""
    new_volume = get_new_volume(
        original_volume=original_volume,
        subtracted_volume=subtracted_volume,
        added_volume=added_volume,
    )
    destination_artifact.udf["Volume (ul)"] = new_volume
    destination_artifact.put()


def set_volumes_from_artifacts(
    artifacts: List[Artifact],
    process_types: List[str],
    lims: Lims,
    subtracted_volume: float,
    added_volume: float,
    sample_artifact: bool = False,
    ignore_fail: bool = False,
) -> None:
    """Set the updated sample volumes on artifact level."""
    failed_artifacts = 0

    for destination_artifact in artifacts:
        try:
            sample = destination_artifact.samples[0]
            if sample_artifact:
                source_artifact = get_sample_artifact(lims=lims, sample=sample)
            else:
                source_artifact = get_latest_analyte(
                    lims=lims,
                    sample_id=sample.id,
                    process_types=process_types,
                    sample_artifact=sample_artifact,
                )
            original_volume = source_artifact.udf.get("Volume (ul)")
            set_updated_sample_volume(
                destination_artifact=destination_artifact,
                original_volume=original_volume,
                subtracted_volume=subtracted_volume,
                added_volume=added_volume,
            )
        except:
            failed_artifacts += 1
    if failed_artifacts and not ignore_fail:
        raise MissingUDFsError(
            message=f"Failed to set artifact UDFs on {failed_artifacts} artifacts. See log for details"
        )


def set_volumes_from_process(
    artifacts: List[Artifact],
    process_types: List[str],
    process_udf: str,
    lims: Lims,
    subtracted_volume: float,
    added_volume: float,
    ignore_fail: bool = False,
) -> None:
    """Set the updated sample volumes on artifact level from a process UDF."""
    failed_artifacts = 0

    for destination_artifact in artifacts:
        try:
            sample = destination_artifact.samples[0]
            artifacts = lims.get_artifacts(samplelimsid=sample.id, process_type=process_types)
            if not artifacts:
                error_message = f"No artifacts found for sample {sample.id} from process types {process_types}, skipping!"
                LOG.info(error_message)
                raise MissingArtifactError(message=error_message)
            latest_artifact = artifacts[-1]
            parent_process = latest_artifact.parent_process
            udf_value = parent_process.udf.get(process_udf)
            set_updated_sample_volume(
                destination_artifact=destination_artifact,
                original_volume=udf_value,
                subtracted_volume=subtracted_volume,
                added_volume=added_volume,
            )
        except MissingArtifactError:
            failed_artifacts += 1
    if failed_artifacts and not ignore_fail:
        raise MissingUDFsError(
            message=f"Failed to set artifact UDFs on {failed_artifacts} artifacts. See log for details"
        )


@click.command()
@options.process_types(help="The process type names from where you want to copy the UDF from.")
@options.sample_artifact(help="Use this flag if you want to copy udf from original artifact")
@options.process_udf(
    help="Optionally fetch the volume from a process UDF. Default is otherwise 'Volume (ul)' on the artifact level."
)
@options.subtract_volume(help="Subtracts volume taken from sample.")
@options.add_volume(help="Adds volume to the total sample amount.")
@options.ignore_fail(help="Add this flag to ignore error exceptions for missing UDFs.")
@click.pass_context
def updated_sample_volume(
    ctx,
    process_types: List[str],
    sample_artifact: bool,
    process_udf: Optional[str],
    subtract_volume: Optional[float] = 0,
    add_volume: Optional[float] = 0,
    ignore_fail: bool = False,
):
    """"""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process = ctx.obj["process"]
    lims = ctx.obj["lims"]

    try:
        artifacts = get_artifacts(process=process)
        if process_udf:
            set_volumes_from_process(
                artifacts=artifacts,
                process_types=process_types,
                process_udf=process_udf,
                lims=lims,
                subtracted_volume=subtract_volume,
                added_volume=add_volume,
                ignore_fail=ignore_fail,
            )
        else:
            set_volumes_from_artifacts(
                artifacts=artifacts,
                process_types=process_types,
                lims=lims,
                sample_artifact=sample_artifact,
                subtracted_volume=subtract_volume,
                added_volume=add_volume,
                ignore_fail=ignore_fail,
            )
        message = "UDFs have been set on all samples."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        sys.exit(e.message)
