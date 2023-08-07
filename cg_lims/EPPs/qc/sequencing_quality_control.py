import sys

import click

from cg_lims.EPPs.qc.sequencing_quality_checker import SequencingQualityChecker
from cg_lims.EPPs.qc.sequencing_artifact_manager import SequencingArtifactManager


@click.command()
@click.pass_context
def sequencing_quality_control(ctx):
    process = ctx.obj["process"]
    status_db_api = ctx.obj["status_db_api"]
    lims = ctx.obj["lims"]

    artifact_manager = SequencingArtifactManager(process=process, lims=lims)

    quality_checker = SequencingQualityChecker(
        artifact_manager=artifact_manager,
        cg_api_client=status_db_api,
    )

    quality_summary: str = quality_checker.validate_sequencing_quality()

    if quality_checker.samples_failed_quality_control():
        sys.exit(quality_summary)

    print(quality_summary, file=sys.stderr)
