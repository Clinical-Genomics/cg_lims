import logging
import sys

import click

from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_qc_output_artifacts
from cg_lims.get.samples import get_one_sample_from_artifact

LOG = logging.getLogger(__name__)


@click.command()
@click.pass_context
def calculate_amount_ng(ctx):
    """Calculates amount of samples for qc validation."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process = ctx.obj["process"]
    lims = ctx.obj["lims"]

    try:
        artifacts = get_qc_output_artifacts(lims=lims, process=process)
        missing_udfs_count = 0
        samples_with_missing_udf = []
        for artifact in artifacts:
            sample = get_one_sample_from_artifact(artifact)
            vol = artifact.udf.get("Volume (ul)")
            conc = artifact.udf.get("Concentration")
            if None in [conc, vol]:
                missing_udfs_count += 1
                samples_with_missing_udf.append(sample.id)
                continue

            artifact.udf["Amount (ng)"] = conc * vol
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
