import click
from genologics.lims import Lims

from cg_lims import options
import logging

LOG = logging.getLogger(__name__)


def search_automations(lims: Lims, search_by: str) -> None:
    """Script to search for Automations.
    The argument search_by could be a script name, eg: bcl2fastq.py,
    or a script argument, eg: CG002 - Aggregate QC (Library Validation).
    """
    LOG.info("AUTOMATION: Searching for '%s'. \n" % search_by)
    automations = lims.get_automations()
    for automation in automations:
        bash_string = automation.string
        if bash_string.find(search_by) == -1:
            continue

        process_ids = [
            (process_type.id, process_type.name) for process_type in automation.process_types
        ]
        LOG.info("Button: %s" % automation.name)
        LOG.info("Bash string: %s" % bash_string)
        LOG.info("Processes: %s \n" % process_ids)


@click.command()
@options.automation_string()
@click.pass_context
def check_config(ctx, automation_string: str):
    """Script to search for Automations.
    The argument search_by could be a script name, eg: bcl2fastq.py,
    or a script argument, eg: CG002 - Aggregate QC (Library Validation).
    """

    lims = ctx.obj["lims"]
    search_automations(search_by=automation_string, lims=lims)
