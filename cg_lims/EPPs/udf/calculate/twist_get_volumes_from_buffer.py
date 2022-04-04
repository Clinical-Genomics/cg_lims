import logging
import sys
from typing import List

import click

from cg_lims import options
from cg_lims.get.artifacts import get_latest_analyte, get_artifacts

LOG = logging.getLogger(__name__)


@click.command()
@options.process_types(help="Get buffer from this process type(s)")
@click.pass_context
def get_volumes_from_buffer(ctx, process_types: List[str]) -> None:
    """Getting Volume Elution from previous step of type defined by process_types.
    If volume found, setting the value Volume udf on artifact of current step.
    As part of the sample is left in the buffer excgange step,
    the value is subtracted by 5 to get the actual volume that is left."""

    LOG.info(f"Running {ctx.command_path} with params {ctx.params}")

    process = ctx.obj["process"]
    lims = ctx.obj["lims"]

    failed_count = 0
    updated_count = 0
    artifacts = get_artifacts(process=process, measurement=True)
    for artifact in artifacts:
        try:
            buffer_artifact = get_latest_analyte(
                lims=lims, sample_id=artifact.samples[0].id, process_types=list(process_types)
            )
        except:
            continue
        if buffer_artifact.udf.get("Volume Elution (ul)"):
            volume_buffer = float(buffer_artifact.udf.get("Volume Elution (ul)")) - 5.0
            if volume_buffer < 0:
                failed_count += 1
                continue
            updated_count += 1
            artifact.udf["Volume (ul)"] = volume_buffer
            artifact.put()

    message = f"Updated {updated_count} samples with volume from Buffer step."
    LOG.info(message)
    click.echo(message)

    if failed_count > 0:
        message = f"Failed to update {failed_count} artifacts - buffer volume lower than 0!"
        LOG.error(message)
        sys.exit(message)
