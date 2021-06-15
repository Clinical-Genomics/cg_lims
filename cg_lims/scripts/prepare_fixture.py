import csv
from pathlib import Path
from typing import List

import click
import yaml
from genologics.lims import Lims, Process
from pydantic import BaseModel, Field


class ProcessFixure(BaseModel):
    samples: Path
    artifacts: Path
    containers: Path
    containertypes: Path
    processes: Path


@click.command()
@click.option("--process")
@click.option("--config")
@click.option("--test_name")
def make_fixure(process: str, test_name: str, config: str):
    with open(config) as file:
        config_data = yaml.load(file, Loader=yaml.FullLoader)
    lims = Lims(config_data["BASEURI"], config_data["USERNAME"], config_data["PASSWORD"])
    process = Process(lims=lims, id=process)
    input_artifacts = process.all_inputs()

    path = Path(f"{test_name}/processes/")
    path.mkdir(parents=True)
    with open(f"{path.absolute()}/{process.id}.xml", "w") as file:
        file.write(str(process.xml()))


if __name__ == "__main__":
    make_fixure()
