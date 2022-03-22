import logging
import click
import pathlib
import yaml
from genologics.lims import Lims

from cg_lims import options

LOG = logging.getLogger(__name__)


@click.command()
@options.config()
@options.log()
def process_to_artifact(
    config: str,
    log: str,
):
    """Script to copy"""

    log_path = pathlib.Path(log)
    log_level = getattr(logging, "INFO")
    logging.basicConfig(filename=str(log_path.absolute()), filemode="w", level=log_level)

    with open(config) as file:
        config_data = yaml.load(file, Loader=yaml.FullLoader)
    lims = Lims(config_data["BASEURI"], config_data["USERNAME"], config_data["PASSWORD"])
    master_step = "Amplify Captured Libraries TWIST v2"
    artifacts = lims.get_artifacts(type="Analyte", process_type=master_step)
    for artifact in artifacts:
        process = artifact.parent_process
        pcr_cycles = process.udf.get("Nr of PCR cycles")
        if pcr_cycles is not None:
            artifact.udf["Nr of PCR cycles"] = str(pcr_cycles)
            artifact.put()
            print(artifact.id)
        else:
            LOG.error(f"process: {process.id} is missing process udf Nr of PCR cycles")


if __name__ == "__main__":
    process_to_artifact()
