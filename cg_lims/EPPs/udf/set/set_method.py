"""Scripts to set the sample date udfs.
"""
import logging
import sys
from typing import List, Optional

import click

import requests
from genologics.entities import Process

from cg_lims import options
from cg_lims.exceptions import LimsError, MissingUDFsError, AtlasResponseFailedError

LOG = logging.getLogger(__name__)


def get_path(document_udf: str, process: Process, atlas_host: str) -> Optional[str]:
    """Get method document path from Atlas"""

    document_title: str = process.udf.get(document_udf)
    if not document_title:
        LOG.warning(f"Process Udf: {document_udf} does not exist or was left empty.")
        return
    response = requests.get(f"{atlas_host}/title/{document_title}/path")
    if response.status_code != 200:
        raise AtlasResponseFailedError(message=f"{response.status_code} : {response.text}")
    return response.json()


def get_document_paths(document_udfs: List[str], process: Process, host: str) -> List[str]:
    """Get method document paths from Atlas"""

    method_documents: List[Optional[str]] = [get_path(udf, process, host) for udf in document_udfs]
    return [doc for doc in method_documents if doc]


def set_methods_and_version(document_udfs: List[str], process: Process, host: str) -> None:
    """Set Method Documents and Atlas Version"""

    method_documents = get_document_paths(document_udfs=document_udfs, host=host, process=process)
    if not method_documents:
        raise MissingUDFsError(message="Found no valid Method document UDFs in the step.")
    response = requests.get(f"{host}/version")
    if response.status_code != 200:
        raise AtlasResponseFailedError(message=f"{response.status_code} : {response.text}")
    process.udf["Methods"] = " ,".join(method_documents)
    process.udf["Atlas Version"] = response.json()
    process.put()
    LOG.info("Method Documents and Atlas Version have been set.")
    click.echo("Method Documents and Atlas Version have been set.")


@click.command()
@options.process_udfs(help="List of Method Document UDFs.")
@click.pass_context
def method_document(ctx: click.Context, process_udfs: List[str]):
    """Script to set method documents and atlas version."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process: Process = ctx.obj["process"]
    atlas_host: str = ctx.obj["atlas_host"]
    try:
        set_methods_and_version(process=process, host=atlas_host, document_udfs=process_udfs)
    except LimsError as e:
        sys.exit(e.message)
