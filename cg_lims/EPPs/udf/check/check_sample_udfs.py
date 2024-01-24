import logging
import sys
from typing import List

import click
from cg_lims import options
from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.get.samples import get_process_samples
from genologics.entities import Process, Sample

LOG = logging.getLogger(__name__)


def check_udfs(samples: List[Sample], sample_udfs: List[str]) -> None:
    """Check that sample UDFs are set."""

    warning = []
    for udf in sample_udfs:
        missing_udfs = [sample.id for sample in samples if sample.udf.get(udf) is None]
        if missing_udfs:
            warning.append(f"UDF: {udf} missing for samples: {missing_udfs}.")
    if warning:
        LOG.warning(" ".join(warning))
        raise MissingUDFsError(message=" ".join(warning))
    LOG.info("Samples UDFs were all set.")


@click.command()
@options.sample_udfs()
@click.pass_context
def check_sample_udfs(ctx: click.Context, sample_udfs: List[str]):
    """Script to check that sample UDFs are set."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process: Process = ctx.obj["process"]
    try:
        samples = get_process_samples(process=process)
        check_udfs(samples=samples, sample_udfs=sample_udfs)
        click.echo("Sample UDFs were checked.")
    except LimsError as e:
        sys.exit(e.message)
