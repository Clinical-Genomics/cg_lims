#!/usr/bin/env python
import click
from cg_lims.EPPs.qc.illumina_sequencing_quality_control import sequencing_quality_control
from cg_lims.EPPs.qc.pacbio_sequencing_quality_control import pacbio_sample_sequencing_metrics
from cg_lims.EPPs.qc.set_qc_fail import set_qc_fail


@click.group(invoke_without_command=True)
@click.pass_context
def qc(ctx):
    """Main entry point of move commands"""
    pass


qc.add_command(set_qc_fail)
qc.add_command(sequencing_quality_control)
qc.add_command(pacbio_sample_sequencing_metrics)
