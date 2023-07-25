import sys

import click

from cg_lims.EPPs.qc.sequencing_quality_checker import SequencingQualityChecker


@click.command()
@click.pass_context
def sequencing_quality_control(ctx):
    process = ctx.obj["process"]
    status_db_api = ctx.obj["status_db_api"]

    quality_checker: SequencingQualityChecker = SequencingQualityChecker(
        process=process, status_db_api=status_db_api
    )
    quality_summary: str = quality_checker.validate_sequencing_quality()

    if quality_checker.samples_failed_quality_control():
        sys.exit(quality_summary)

    print(quality_summary, file=sys.stderr)
