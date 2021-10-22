import logging
from typing import List

import click
from genologics.lims import Process, Sample
import requests
from requests import Response
import json
from cg_lims.exceptions import LimsError
from cg_lims.get.samples import get_process_samples
from cg_lims.models.arnold.sample import ArnoldSample

LOG = logging.getLogger(__name__)


@click.command()
@click.pass_context
def sample(ctx):
    """Creating Sample documents in the arnold Sample collection."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process: Process = ctx.obj["process"]
    arnold_host: str = ctx.obj["arnold_host"]
    samples: List[Sample] = get_process_samples(process=process)

    sample_documents = []
    for sample in samples:
        arnold_sample = ArnoldSample(**dict(sample.udf.items()), sample_id=sample.id, id=sample.id)
        sample_documents.append(arnold_sample.dict(exclude_none=True))

    response: Response = requests.put(
        url=f"{arnold_host}/samples",
        headers={"Content-Type": "application/json"},
        data=json.dumps(sample_documents),
    )
    if not response.ok:
        LOG.info(response.text)
        raise LimsError(response.text)

    LOG.info("Arnold output: %s", response.text)
    click.echo("Sample documents inserted to arnold database")
