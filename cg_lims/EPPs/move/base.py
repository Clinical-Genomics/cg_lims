#!/usr/bin/env python
import click

from cg_lims.EPPs.move.move_samples import move_samples
from cg_lims.EPPs.move.place_samples_in_seq_agg import place_samples_in_seq_agg

# commands
from cg_lims.EPPs.move.rerun_samples import rerun_samples


@click.group(invoke_without_command=True)
@click.pass_context
def move(ctx):
    """Main entry point of move commands"""
    pass


move.add_command(rerun_samples)
move.add_command(move_samples)
move.add_command(place_samples_in_seq_agg)
