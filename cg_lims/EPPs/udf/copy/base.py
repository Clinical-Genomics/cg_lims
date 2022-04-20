#!/usr/bin/env python

import click

# commands
from cg_lims.EPPs.udf.copy.artifact_to_sample import artifact_to_sample
from cg_lims.EPPs.udf.copy.sample_to_artifact import sample_to_artifact
from cg_lims.EPPs.udf.copy.process_to_sample import process_to_sample
from cg_lims.EPPs.udf.copy.reads_to_sequence import reads_to_sequence
from cg_lims.EPPs.udf.copy.artifact_to_artifact import artifact_to_artifact
from cg_lims.EPPs.udf.copy.process_to_artifact import process_to_artifact
from cg_lims.EPPs.udf.copy.qc_to_sample import qc_to_sample
from cg_lims.EPPs.udf.copy.original_well_to_sample import original_position_to_sample
from cg_lims.EPPs.udf.copy.aggregate_qc_flags_and_copy_fields import aggregate_qc_and_copy_fields

@click.group(invoke_without_command=True)
@click.pass_context
def copy(ctx):
    """Main entry point of copy commands"""
    pass


copy.add_command(artifact_to_sample)
copy.add_command(sample_to_artifact)
copy.add_command(process_to_sample)
copy.add_command(reads_to_sequence)
copy.add_command(artifact_to_artifact)
copy.add_command(process_to_artifact)
copy.add_command(qc_to_sample)
copy.add_command(original_position_to_sample)
copy.add_command(aggregate_qc_and_copy_fields)
