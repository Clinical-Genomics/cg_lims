import logging
import sys

import click
from cg_lims.clients.cg.status_db_api import StatusDBAPI
from cg_lims.EPPs.qc.sequencing_artifact_manager import PacbioSequencingArtifactManager
from cg_lims.EPPs.qc.sequencing_quality_checker import PacBioSequencingQualityChecker
from cg_lims.exceptions import LimsError
from genologics.entities import Process
from genologics.lims import Lims

LOG = logging.getLogger(__name__)


@click.command()
@click.pass_context
def pacbio_sample_sequencing_metrics(ctx):
    """Script for fetching PacBio sample sequencing results from StatusDB and set corresponding artifact UDFs."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process: Process = ctx.obj["process"]
    lims: Lims = ctx.obj["lims"]
    status_db_api: StatusDBAPI = ctx.obj["status_db"]

    try:
        artifact_manager: PacbioSequencingArtifactManager = PacbioSequencingArtifactManager(
            process=process, lims=lims
        )

        quality_checker: PacBioSequencingQualityChecker = PacBioSequencingQualityChecker(
            artifact_manager=artifact_manager,
            cg_api_client=status_db_api,
        )

        quality_summary: str = quality_checker.validate_sequencing_quality(lims=lims)
        brief_summary: str = quality_checker.get_brief_summary()

        if quality_checker.samples_failed_quality_control():
            LOG.error(quality_summary)
            sys.exit(brief_summary)

        LOG.info(quality_summary)
        click.echo(brief_summary)

    except LimsError as e:
        sys.exit(e.message)
