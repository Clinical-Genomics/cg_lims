import logging
import sys
from typing import List

import click
from genologics.entities import Artifact

from cg_lims.adapter.plugin import get_cg_lims_adapter
from cg_lims.exceptions import LimsError
from cg_lims.get.artifacts import get_artifacts
from cg_lims.get.workflow import get_workflow
from cg_lims.models.database.prepp import PrepCollectionWGSPCRFree
from cg_lims.crud.create import create_preps

LOG = logging.getLogger(__name__)


def build_document(artifact: Artifact, workflow: str):
    """Building a PrepCollectionWGSPCRFree document."""

    sample_ids: List[str] = [sample.id for sample in artifact.samples]

    return PrepCollectionWGSPCRFree(
        _id=artifact.id,
        workflow=workflow,
        prep_id=artifact.id,
        sample_ids=sample_ids,
        test_field="some_str",
    )


@click.command()
@click.pass_context
def wgs_prep_document(ctx):
    """Creating PrepCollectionWGSPCRFree documents in the prep collection."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")

    process = ctx.obj["process"]
    workflow = get_workflow(process)
    adapter = get_cg_lims_adapter(db_uri=ctx.obj["db_uri"], db_name=ctx.obj["db_name"])
    try:
        artifacts: List[Artifact] = get_artifacts(process=process, input=True)
        prep_documents: List[PrepCollectionWGSPCRFree] = [
            build_document(artifact=artifact, workflow=workflow) for artifact in artifacts
        ]
        document_ids: List[str] = create_preps(adapter=adapter, preps=prep_documents)
        document_ids_str = [str(document_id) for document_id in document_ids]
        message = f"Created documents {' ,'.join(document_ids_str)} in prep collection"
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
