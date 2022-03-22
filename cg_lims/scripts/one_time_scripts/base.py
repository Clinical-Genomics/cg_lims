#!/usr/bin/env python

import click

from .load_arnold_preps import load_arnold_preps


@click.group(invoke_without_command=True)
@click.pass_context
def one_time(ctx):
    """Main load commands."""
    pass


one_time.add_command(load_arnold_preps)
