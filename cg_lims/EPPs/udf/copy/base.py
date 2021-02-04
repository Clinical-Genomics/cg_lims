#!/usr/bin/env python

import click

# commands
from cg_lims.EPPs.udf.copy.artifact_to_sample import artifact_to_sample
from cg_lims.EPPs.udf.copy.sample_to_artifact import sample_to_artifact


@click.group(invoke_without_command=True)
@click.pass_context
def copy(ctx):
    """Main entry point of copy commands"""
    pass


copy.add_command(artifact_to_sample)
copy.add_command(sample_to_artifact)
