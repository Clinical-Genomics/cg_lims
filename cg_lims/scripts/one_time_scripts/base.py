#!/usr/bin/env python

import click

from .load_arnold_steps import update_arnold_preps, update_arnold_runs
from .load_arnold_flowcells import update_arnold_flow_cells
from .fetch_tga_samples import fetch_tga_samples


@click.group(invoke_without_command=True)
@click.pass_context
def one_time(ctx):
    """Main load commands."""


one_time.add_command(update_arnold_preps)
one_time.add_command(update_arnold_runs)
one_time.add_command(update_arnold_flow_cells)
one_time.add_command(fetch_tga_samples)
