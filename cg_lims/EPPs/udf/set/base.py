import click

from cg_lims.EPPs.udf.set.set_samples_reads_missing import set_reads_missing_on_new_samples
from cg_lims.EPPs.udf.set.set_sample_date import (
    set_delivered,
    set_sequenced,
    set_prepared,
    set_received,
)


@click.group(invoke_without_command=True)
@click.pass_context
def set(context: click.Context):
    """Main entry point of set commands"""
    pass


set.add_command(set_reads_missing_on_new_samples)
set.add_command(set_delivered)
set.add_command(set_sequenced)
set.add_command(set_prepared)
set.add_command(set_received)
