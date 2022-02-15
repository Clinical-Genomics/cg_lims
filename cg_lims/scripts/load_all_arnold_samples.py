import logging
from typing import List

import click
from genologics.lims import Sample, Lims
import requests
from requests import Response
import json
from cg_lims.exceptions import LimsError
from cg_lims.models.arnold.sample import ArnoldSample

LOG = logging.getLogger(__name__)


@click.command()
@click.pass_context
def load_all_samples(ctx):
    """Creating Sample documents in the arnold Sample collection."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    lims: Lims = ctx.obj["lims"]
    arnold_host: str = ctx.obj["arnold_host"]
    samples: List[Sample] = lims.get_samples()
    print(len(samples))
    sample_documents = []
    for sample in samples:
        try:
            arnold_sample = ArnoldSample(
                **dict(sample.udf.items()),
                sample_id=sample.id,
                id=sample.id,
                ticket=sample.project.name,
            )
            sample_documents.append(arnold_sample.dict(exclude_none=True))
        except:
            print(sample)
    print(len(sample_documents))
    print("ready to load")
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
