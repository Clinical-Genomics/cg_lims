import logging
import sys

import click
from requests.exceptions import ConnectionError

from cg_lims.exceptions import LimsError, MissingCgFieldError
from cg_lims.get.artifacts import get_artifacts

LOG = logging.getLogger(__name__)


def missing_reads(artifacts: list, status_db) -> tuple:
    failed_arts = 0
    passed_arts = 0
    for art in artifacts:
        samples = art.samples
        try:
            reads_total = samples[0].udf["Total Reads (M)"]
            app_tag = samples[0].udf["Sequencing Analysis"]
        except:
            failed_arts += 1
            continue
        try:
            target_amount_reads = status_db.apptag(tag_name=app_tag, key="target_reads")
            guaranteed_fraction = 0.01 * status_db.apptag(
                tag_name=app_tag, key="percent_reads_guaranteed"
            )
        except ConnectionError:
            raise LimsError(message="Could not communicate with cg server")
        except:
            raise MissingCgFieldError(f"Could not find application tag: {app_tag} in database.")
        # Converting from reads to million reads.
        target_amount = target_amount_reads / 1000000
        reads_min = target_amount * guaranteed_fraction
        reads_missing = reads_min - reads_total
        if reads_missing > 0:
            for sample in samples:
                sample.udf["Reads missing (M)"] = target_amount - reads_total
                sample.put()
            art.udf["Rerun"] = True
            art.qc_flag = "FAILED"
        else:
            for sample in samples:
                sample.udf["Reads missing (M)"] = 0
                sample.put()
            art.udf["Rerun"] = False
            art.qc_flag = "PASSED"
        art.put()
        passed_arts += 1
    return passed_arts, failed_arts


@click.command()
@click.pass_context
def get_missing_reads(ctx):
    """Script to calculate missing reads and decide on reruns"""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process = ctx.obj["process"]
    status_db = ctx.obj["status_db"]

    try:
        artifacts = get_artifacts(process=process, input=False)
        passed_arts, failed_arts = missing_reads(artifacts=artifacts, status_db=status_db)
        message = f"Updataed {passed_arts}. Ignored {failed_arts} due to missing UDFs"
        if failed_arts:
            LOG.error(message)
            sys.exit(message)
        else:
            LOG.info(message)
            click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
