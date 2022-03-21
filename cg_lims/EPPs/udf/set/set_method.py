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


def get_path(document_title: str, process: Process, atlas_host: str) -> str:
    """Get method document path from Atlas"""

    response = requests.get(f"{atlas_host}/title/{document_title}/path")
    if response.status_code != 200:
        raise AtlasResponseFailedError(message=f"{response.status_code} : {response.text}")
    return response.json()


def get_document_paths(document_udfs: List[str], process: Process, host: str) -> List[str]:
    """Get method document paths from Atlas"""
    method_documents = []
    for udf in document_udfs:
        document_title: str = process.udf.get(udf)
        if not document_title or (document_title == "Manual"):
            LOG.warning(f"Process Udf: {udf} does not exist, was left empty or was set to Manual.")
            continue
        document_path = get_path(document_title, process, host)
        if document_path:
            method_documents.append(document_path)
    return method_documents


def set_methods_and_version(method_documents: List[str], process: Process, host: str) -> None:
    """Set Method Documents and Atlas Version"""

    response = requests.get(f"{host}/version")
    if response.status_code != 200:
        raise AtlasResponseFailedError(f"{response.status_code} : {response.text}")
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
        method_documents = get_document_paths(
            document_udfs=process_udfs, host=atlas_host, process=process
        )
        if not method_documents:
            LOG.info(msg="Found no valid Method document UDFs in the step.")
            click.echo("Found no Method document UDFs in the step.")
        else:
            set_methods_and_version(
                process=process, host=atlas_host, method_documents=method_documents
            )
    except LimsError as e:
        sys.exit(e.message)
