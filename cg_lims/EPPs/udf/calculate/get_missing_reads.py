import logging
import sys
import click

from cg_lims.exceptions import LimsError, MissingFieldError
from cg_lims.get.artifacts import get_artifacts

LOG = logging.getLogger(__name__)


def get_missing_reads(artifacts):
    failed_arts = 0
    passed_arts = 0
    for art in artifacts:
        samples = art.samples
        try:
            reads_total = samples[0].udf['Total Reads (M)']
            app_tag = samples[0].udf['Sequencing Analysis']
        except:
            failed_arts += 1
            continue
        try:
            target_amount_reads = cgface_obj.apptag(tag_name=app_tag, key='target_reads')
            guaranteed_fraction = cgface_obj.apptag(tag_name=app_tag, key='reads_guaranteed')
        except:
            raise MissingFieldError(f"Could not find application tag: {app_tag} in database.")
        # Converting from reads to million reads.
        target_amount = target_amount_reads / 1000000
        reads_min = target_amount * guaranteed_fraction
        reads_missing = reads_min - reads_total
        if reads_missing > 0:
            for sample in samples:
                sample.udf['Reads missing (M)'] = target_amount - reads_total
                sample.put()
            art.udf['Rerun'] = True
            art.qc_flag = 'FAILED'
        else:
            for sample in samples:
                sample.udf['Reads missing (M)'] = 0
                sample.put()
            art.udf['Rerun'] = False
            art.qc_flag = 'PASSED'
        art.put()
        passed_arts += 1


@click.command()
@click.pass_context
def get_missing_reads(ctx):
    """"""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process = ctx.obj["process"]

    try:
        artifacts = get_artifacts(process=process, input=False)
        message = get_missing_reads(artifacts=artifacts)
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)