from typing import List, Optional
from genologics.entities import Artifact
from genologics.lims import Lims

from cg_lims.get.artifacts import get_latest_analyte
from cg_lims import options
from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts

import logging
import sys
import click

LOG = logging.getLogger(__name__)


def get_new_volume(source_artifact: Artifact, subtracted_volume: float) -> float:
    """Calculate the updated volume of a sample."""
    original_volume = source_artifact.udf.get("Volume (ul)")
    return float(original_volume) - float(subtracted_volume)


def set_updated_sample_volume(
    destination_artifact: Artifact, source_artifact: Artifact, subtracted_volume: float
) -> None:
    """"""
    new_volume = get_new_volume(
        source_artifact=source_artifact, subtracted_volume=subtracted_volume
    )
    print(new_volume)
    destination_artifact.udf["Volume (ul)"] = new_volume
    destination_artifact.put()


def set_all_updated_sample_volumes(
    artifacts: List[Artifact],
    process_types: List[str],
    lims: Lims,
    sample_artifact: bool = False,
    subtracted_volume: float = 0,
) -> None:
    """Set the updated sample volumes on artifact level."""
    failed_artifacts = 0

    for destination_artifact in artifacts:
        try:
            sample = destination_artifact.samples[0]
            source_artifact = get_latest_analyte(
                lims=lims,
                sample_id=sample.id,
                process_types=process_types,
                sample_artifact=sample_artifact,
            )
            set_updated_sample_volume(
                destination_artifact=destination_artifact,
                source_artifact=source_artifact,
                subtracted_volume=subtracted_volume,
            )
        except:
            failed_artifacts += 1
    if failed_artifacts:
        raise MissingUDFsError(
            message=f"Failed to set artifact udfs on {failed_artifacts} artifacts. See log for details"
        )


@click.command()
@options.process_types(help="The process type names from where you want to copy the artifact udf.")
@options.sample_artifact(help="Use this flag if you want to copy udf from original artifact")
@options.subtract_volume(help="Subtracts volume taken from sample.")
@click.pass_context
def updated_sample_volume(
    ctx, process_types: List[str], sample_artifact: bool, subtract_volume: Optional[float]
):
    """"""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process = ctx.obj["process"]
    lims = ctx.obj["lims"]

    try:
        artifacts = get_artifacts(process=process)
        set_all_updated_sample_volumes(
            artifacts=artifacts,
            process_types=process_types,
            lims=lims,
            sample_artifact=sample_artifact,
            subtracted_volume=subtract_volume,
        )
        click.echo("UDFs have been set on all samples.")
    except LimsError as e:
        sys.exit(e.message)
