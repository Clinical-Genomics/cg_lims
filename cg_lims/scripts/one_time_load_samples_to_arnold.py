import csv
from pathlib import Path
from typing import List

import click
import yaml
from genologics.entities import Artifact, Sample, Entity
from genologics.lims import Lims, Process
from pydantic import BaseModel, Field
import click
import requests
from requests import Response
import json

import logging


from cg_lims.models.arnold import ArnoldSample


@click.command()
@click.option("--config")
def load_samples(config: str):
    logging.basicConfig(filename="sample.log", level=logging.DEBUG)
    with open(config) as file:
        config_data = yaml.load(file, Loader=yaml.FullLoader)
    lims = Lims(config_data["BASEURI"], config_data["USERNAME"], config_data["PASSWORD"])
    arnold_host = config_data["ARNOLD_HOST"]

    lims_samples = lims.get_samples()

    for sample in lims_samples:
        try:
            sample_id = sample.id
            arnold_sample = ArnoldSample(
                **dict(sample.udf.items()), sample_id=sample.id, id=sample_id
            )
            response: Response = requests.put(
                url=f"{arnold_host}/sample",
                headers={"Content-Type": "application/json"},
                data=json.dumps(arnold_sample.dict(exclude_none=True)),
            )
            logging.info(f"Loaded sample {sample_id}")
            print("ja")
        except:
            print("nejq")
            logging.error(f"failed sample {sample_id}")


if __name__ == "__main__":
    load_samples()
