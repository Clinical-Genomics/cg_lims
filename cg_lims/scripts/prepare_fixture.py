import csv
from pathlib import Path
from typing import List

import click
import yaml
from genologics.entities import Artifact, Sample, Entity
from genologics.lims import Lims, Process
from pydantic import BaseModel, Field


class ProcessFixure(BaseModel):
    samples: Path
    artifacts: Path
    containers: Path
    containertypes: Path
    processes: Path


def replace_str(file: Path, replace: str, replace_with: str) -> None:
    file.write_text(file.read_text().replace(replace, replace_with))


def build_file_structure(base_dir: str) -> ProcessFixure:
    processes = Path(f"{base_dir}/processes/")
    processes.mkdir(parents=True)
    artifacts = Path(f"{base_dir}/artifacts/")
    artifacts.mkdir(parents=True)
    containers = Path(f"{base_dir}/containers/")
    containers.mkdir(parents=True)
    containertypes = Path(f"{base_dir}/containertypes/")
    containertypes.mkdir(parents=True)
    samples = Path(f"{base_dir}/samples/")
    samples.mkdir(parents=True)
    return ProcessFixure(
        samples=samples,
        processes=processes,
        artifacts=artifacts,
        containers=containers,
        containertypes=containertypes,
    )


def add_file(entity: Entity, entity_dir: Path) -> None:
    new_file = Path(f"{entity_dir.absolute()}/{entity.id}.xml")
    with open(new_file.absolute(), "wb") as file:
        file.write(entity.xml())
    replace_str(
        file=new_file,
        replace="clinical-lims-stage.scilifelab.se",
        replace_with="127.0.0.1:8000",
    )


def add_entities(entities: List[Entity], entity_dir: Path):
    for entity in entities:
        entity.get()
        add_file(entity=entity, entity_dir=entity_dir)


@click.command()
@click.option("--process")
@click.option("--config")
@click.option("--test_name")
def make_fixure(process: str, test_name: str, config: str):
    with open(config) as file:
        config_data = yaml.load(file, Loader=yaml.FullLoader)
    lims = Lims(config_data["BASEURI"], config_data["USERNAME"], config_data["PASSWORD"])

    process = Process(lims=lims, id=process)
    process.get()
    fixture_dir: ProcessFixure = build_file_structure(base_dir=test_name)
    add_file(entity=process, entity_dir=fixture_dir.processes)
    artifacts = process.all_inputs() + process.all_outputs()
    add_entities(entities=artifacts, entity_dir=fixture_dir.artifacts)
    samples = []
    for artifact in artifacts:
        samples += artifact.samples
    add_entities(entities=samples, entity_dir=fixture_dir.samples)


if __name__ == "__main__":
    make_fixure()
