import logging
import sys

import click

from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_qc_output_artifacts
from cg_lims.get.samples import get_one_sample_from_artifact
from cg_lims import options

LOG = logging.getLogger(__name__)


@click.command()
@options.concentration_keyword_option()
@options.amount_keyword_option()
@options.volume_keyword_option()
@click.pass_context
def calculate_amount_ng(
    ctx: click.Context, amount_keyword: str, volume_keyword: str, concentration_keyword: str
):
    """Calculates and auto-fills the quantities of DNA in sample from concentration and volume measurements"""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process = ctx.obj["process"]
    lims = ctx.obj["lims"]

    try:
        artifacts = get_qc_output_artifacts(lims=lims, process=process)
        missing_udfs_count = 0
        samples_with_missing_udf = []
        for artifact in artifacts:
            sample = get_one_sample_from_artifact(artifact)
            vol = artifact.udf.get(volume_keyword)
            conc = artifact.udf.get(concentration_keyword)
            if None in [conc, vol]:
                missing_udfs_count += 1
                samples_with_missing_udf.append(sample.id)
                continue

            artifact.udf[amount_keyword] = conc * vol
            artifact.put()
        if missing_udfs_count:
            raise MissingUDFsError(
                f"Udf missing for {missing_udfs_count} sample(s): {','.join(samples_with_missing_udf)}."
            )
        message = "Amounts have been calculated for all samples."
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
