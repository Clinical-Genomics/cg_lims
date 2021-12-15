"""Scripts to set the sample date udfs.
"""
import logging
import sys
from typing import List

import click

import requests
from genologics.entities import Process

from cg_lims import options
from cg_lims.exceptions import LimsError, MissingUDFsError

LOG = logging.getLogger(__name__)


def get_document_paths(document_udfs: List[str], process: Process, atlas_host: str) -> List[str]:
    """Get method document paths from Atlas"""
    method_documents = []
    for document_udf in document_udfs:
        document_title: str = process.udf.get(document_udf)
        if not document_title:
            LOG.warning(f"Process Udf: {document_udf} does not exist or was left empty.")
            continue
        response = requests.get(f"{atlas_host}/title/{document_title}/path")
        if response.status_code != 200:
            raise response  ##something
        method_documents.append(response.json())

    if not method_documents:
        raise MissingUDFsError(message="Found no valid Method document UDFs in the step.")

    return method_documents


@click.command()
@options.process_udfs(help="List of Method Document UDFs.")
@click.pass_context
def method_document(ctx: click.Context, process_udfs: List[str]):
    """Script to set method documents and atlas version."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process: Process = ctx.obj["process"]
    atlas_host: str = ctx.obj["atlas_host"]

    try:
        atlas_version = requests.get(f"{atlas_host}/version")
        method_documents = get_document_paths(
            document_udfs=process_udfs, atlas_host=atlas_host, process=process
        )
        process.udf["Methods"] = " ,".join(method_documents)
        process.udf["Atlas Version"] = atlas_version.json()
        process.put()
        LOG.info("Method Documents and Atlas Version have been set.")
        click.echo("Method Documents and Atlas Version have been set.")
    except LimsError as e:
        sys.exit(e.message)
