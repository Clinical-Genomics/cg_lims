import click
from cg_lims.EPPs.udf.set.replace_flow_cell_output_path import replace_flow_cell_output_path
from cg_lims.EPPs.udf.set.set_barcode import assign_barcode
from cg_lims.EPPs.udf.set.set_method import method_document
from cg_lims.EPPs.udf.set.set_sample_date import set_sample_date
from cg_lims.EPPs.udf.set.set_samples_reads_missing import set_reads_missing_on_new_samples
from cg_lims.EPPs.udf.set.set_sequencing_settings import set_sequencing_settings


@click.group(invoke_without_command=True)
@click.pass_context
def set(context: click.Context):
    """Main entry point of set commands"""
    pass


set.add_command(set_reads_missing_on_new_samples)
set.add_command(set_sample_date)
set.add_command(method_document)
set.add_command(assign_barcode)
set.add_command(set_sequencing_settings)
set.add_command(replace_flow_cell_output_path)
