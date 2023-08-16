#!/usr/bin/env python
import click
from cg_lims.EPPs.qc.sequencing_quality_control import sequencing_quality_control
from cg_lims.EPPs.qc.set_qc_fail import set_qc_fail


@click.group(invoke_without_command=True)
@click.pass_context
def qc(ctx):
    """Main entry point of move commands"""
    pass


qc.add_command(set_qc_fail)
qc.add_command(sequencing_quality_control)
