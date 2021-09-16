import click

from cg_lims.EPPs.udf.set.set_samples_reads_missing import set_reads_missing_on_new_samples


@click.group(invoke_without_command=True)
@click.pass_context
def set(context: click.Context):
    """Main entry point of set commands"""
    pass


set.add_command(set_reads_missing_on_new_samples)
