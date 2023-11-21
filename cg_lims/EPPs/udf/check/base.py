#!/usr/bin/env python

import click

# commands
from cg_lims.EPPs.udf.check.check_artifact_udfs import check_artifact_udfs
from cg_lims.EPPs.udf.check.check_process_udfs import check_process_udfs


@click.group(invoke_without_command=True)
@click.pass_context
def check(ctx):
    """Main entry point of check commands"""
    pass


check.add_command(check_artifact_udfs)
check.add_command(check_process_udfs)
