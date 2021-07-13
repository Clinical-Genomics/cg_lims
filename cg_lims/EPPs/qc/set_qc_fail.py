import click
from genologics.entities import Process


@click.command()
@click.pass_context
def set_qc_fail(ctx):
    process = ctx.obj["process"]
    lims = ctx.obj["lims"]

    qc_process_id = process.udf.get("QC Process ID")
    process = Process(lims=lims, id=qc_process_id)
    artifacts = process.all_outputs(unique=True)
    for artifact in artifacts:
        artifact.qc_flag = "FAILED"
        artifact.put()
    click.echo("QC-flags have been set.")
