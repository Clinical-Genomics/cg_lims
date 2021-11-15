import logging
import sys

import click

from cg_lims import options
from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_qc_output_artifacts

LOG = logging.getLogger(__name__)


@click.command()
@options.concentration_udf_option()
@options.amount_udf_option()
@options.volume_udf_option()
@options.subtract_volume_option()
@click.pass_context
def calculate_amount_ng(
    ctx: click.Context,
    amount_udf: str,
    volume_udf: str,
    concentration_udf: str,
    subtract_volume: str,
):
    """Calculates and auto-fills the quantities of DNA in sample from concentration and volume
    measurements. The volume is subtracted by either 0 or 3 in the calculations. This is
    because the lab uses 0 or 3 ul in the initial qc measurements."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process = ctx.obj["process"]
    lims = ctx.obj["lims"]

    try:
        artifacts = get_qc_output_artifacts(lims=lims, process=process)
        missing_udfs_count = 0
        artifacts_with_missing_udf = []
        for artifact in artifacts:
            vol = artifact.udf.get(volume_udf)
            conc = artifact.udf.get(concentration_udf)
            if None in [conc, vol]:
                missing_udfs_count += 1
                artifacts_with_missing_udf.append(artifact.id)
                continue

            artifact.udf[amount_udf] = conc * (vol - int(subtract_volume))
            artifact.put()
        if missing_udfs_count:
            raise MissingUDFsError(
                f"Udf missing for {missing_udfs_count} artifact(s): "
                f"{','.join(artifacts_with_missing_udf)}. "
            )
        message = "Amounts have been calculated for all artifacts."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
