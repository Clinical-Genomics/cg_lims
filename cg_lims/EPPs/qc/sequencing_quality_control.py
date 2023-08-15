import sys

import click

import logging

from cg_lims.EPPs.qc.sequencing_quality_checker import SequencingQualityChecker
from cg_lims.EPPs.qc.sequencing_artifact_manager import SequencingArtifactManager

LOG = logging.getLogger(__name__)


@click.command()
@click.pass_context
def sequencing_quality_control(ctx):
    """Sequencing quality control script for the BCL conversion step in LIMS."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process = ctx.obj["process"]
    status_db_api = ctx.obj["status_db"]
    lims = ctx.obj["lims"]

    artifact_manager = SequencingArtifactManager(process=process, lims=lims)

    quality_checker = SequencingQualityChecker(
        artifact_manager=artifact_manager,
        cg_api_client=status_db_api,
    )

    quality_summary: str = quality_checker.validate_sequencing_quality()

    if quality_checker.samples_failed_quality_control():
        LOG.error(quality_summary)
        sys.exit(quality_summary)

    LOG.info(quality_summary)
    click.echo(quality_summary)
