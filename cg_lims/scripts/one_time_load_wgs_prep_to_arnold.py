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

from cg_lims.EPPs.arnold.prep import build_step_documents
from cg_lims.models.arnold import ArnoldSample


@click.command()
@click.option("--config")
def load_preps(config: str):
    logging.basicConfig(filename="wgs.log", level=logging.DEBUG)
    with open(config) as file:
        config_data = yaml.load(file, Loader=yaml.FullLoader)
    lims = Lims(config_data["BASEURI"], config_data["USERNAME"], config_data["PASSWORD"])
    arnold_host = config_data["ARNOLD_HOST"]

    processes = lims.get_processes(type="Aggregate QC (Library Validation)")

    for process in processes:
        try:
            all_step_documents = build_step_documents(prep_type="wgs", process=process, lims=lims)
            response: Response = requests.post(
                url=f"{arnold_host}/steps",
                headers={"Content-Type": "application/json"},
                data=json.dumps([doc.dict(exclude_none=True) for doc in all_step_documents]),
            )

            logging.info(f"Loaded process {process.id}")
        except:
            logging.error(f"failed process {process.id}")


if __name__ == "__main__":
    load_preps()
