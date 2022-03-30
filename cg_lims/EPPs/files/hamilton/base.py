import click

# commands
from cg_lims.EPPs.files.hamilton.normalization_file import barcode_file
from cg_lims.EPPs.files.hamilton.make_kapa_csv import make_kapa_csv
from cg_lims.EPPs.files.hamilton.sars_cov2_prep_file import sars_cov2_prep_file
from cg_lims.EPPs.files.hamilton.buffer_exchange_twist_file import buffer_exchange_twist_file


@click.group(invoke_without_command=True)
@click.pass_context
def hamilton(ctx):
    """Main entry point of hamilton file commands"""
    pass


hamilton.add_command(make_kapa_csv)
hamilton.add_command(barcode_file)
hamilton.add_command(sars_cov2_prep_file)
hamilton.add_command(buffer_exchange_twist_file)
