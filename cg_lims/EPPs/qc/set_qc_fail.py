import click
from genologics.entities import Process


@click.command()
@click.pass_context
def set_qc_fail(ctx):
    """Helper script for procudtion so set qc-flaggs to failed after the step has been closed.

    The script will set qc flagg to failed on all artifacts within a process,
     where the process is defined by the udf "QC Process ID".
     The script is supposed to be run from within a script process."""

    process = ctx.obj["process"]
    lims = ctx.obj["lims"]

    qc_process_id = process.udf.get("QC Process ID")
    qc_process = Process(lims=lims, id=qc_process_id)
    artifacts = qc_process.all_outputs(unique=True)
    for artifact in artifacts:
        artifact.qc_flag = "FAILED"
        artifact.put()
    click.echo("QC-flags have been set.")
    process.udf["QC Process ID"] = ""
    process.put()
