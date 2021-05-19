import click
import yaml
from genologics.lims import Lims
from genologics.entities import Process

from cg_lims.get.artifacts import get_artifacts


@click.command()
@click.option("--config")
@click.option("--process")
def set_qc_fail(config: str, process: str):
    with open(config) as file:
        config_data = yaml.load(file, Loader=yaml.FullLoader)
    lims = Lims(config_data["BASEURI"], config_data["USERNAME"], config_data["PASSWORD"])
    process = Process(lims=lims, id=process)
    artifacts = process.all_outputs(unique=True)
    for artifact in artifacts:
        artifact.qc_flag = "FAILED"
        artifact.put()
    click.echo("QC-flags have been set.")


if __name__ == "__main__":
    set_qc_fail()
