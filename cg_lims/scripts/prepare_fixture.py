from pathlib import Path
from typing import List, Optional, Set

import click
from genologics.entities import Artifact, Container, Containertype, Entity, Process, Sample
from genologics.lims import Lims
from pydantic.v1 import BaseModel


class ProcessFixture(BaseModel):
    samples: Path
    artifacts: Path
    containers: Path
    containertypes: Path
    processtypes: Path
    processes: Path


def replace_str(file: Path, replace: str, replace_with: str) -> None:
    file.write_text(file.read_text().replace(replace, replace_with))


def build_file_structure(base_dir: str) -> ProcessFixture:
    processes: Path = Path(f"{base_dir}/processes/")
    if not processes.exists():
        processes.mkdir(parents=True)
    processtypes: Path = Path(f"{base_dir}/processtypes/")
    if not processtypes.exists():
        processtypes.mkdir(parents=True)
    artifacts: Path = Path(f"{base_dir}/artifacts/")
    if not artifacts.exists():
        artifacts.mkdir(parents=True)
    containers: Path = Path(f"{base_dir}/containers/")
    if not containers.exists():
        containers.mkdir(parents=True)
    containertypes: Path = Path(f"{base_dir}/containertypes/")
    if not containertypes.exists():
        containertypes.mkdir(parents=True)
    samples: Path = Path(f"{base_dir}/samples/")
    if not samples.exists():
        samples.mkdir(parents=True)
    return ProcessFixture(
        samples=samples,
        processes=processes,
        artifacts=artifacts,
        containers=containers,
        containertypes=containertypes,
        processtypes=processtypes,
    )


def add_file(entity: Entity, entity_dir: Path) -> None:
    new_file: Path = Path(f"{entity_dir.absolute()}/{entity.id}.xml")
    lims: Lims = entity.lims
    base_uri: str = lims.baseuri
    with open(new_file.absolute(), "wb") as file:
        file.write(entity.xml())
    replace_str(
        file=new_file,
        replace=base_uri,
        replace_with="http://127.0.0.1:8000/",
    )


def add_entities(entities: List[Entity], entity_dir: Path):
    for entity in entities:
        entity.get()
        add_file(entity=entity, entity_dir=entity_dir)


@click.command()
@click.option("--process")
@click.option("--test_name")
@click.pass_context
def make_fixture(ctx, process: str, test_name: str):
    lims: Lims = ctx.obj["lims"]
    process: Process = Process(lims=lims, id=process)
    process.get()
    fixture_dir: ProcessFixture = build_file_structure(base_dir=test_name)
    add_file(entity=process, entity_dir=fixture_dir.processes)
    add_file(entity=process.type, entity_dir=fixture_dir.processtypes)
    artifacts: List[Artifact] = process.all_inputs() + process.all_outputs()
    add_entities(entities=artifacts, entity_dir=fixture_dir.artifacts)
    samples: List[Sample] = []
    for artifact in artifacts:
        samples += artifact.samples
    add_entities(entities=samples, entity_dir=fixture_dir.samples)
    containers: Set[Optional[Container]] = {artifact.location[0] for artifact in artifacts}
    if None in containers:
        containers.remove(None)
    add_entities(entities=list(containers), entity_dir=fixture_dir.containers)
    container_types: List[Containertype] = list({container.type for container in containers})
    add_entities(entities=container_types, entity_dir=fixture_dir.containertypes)
