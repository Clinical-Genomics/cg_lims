#!/usr/bin/env python
from typing import Tuple

from genologics.entities import Process, Artifact
from genologics.lims import Lims

from cg_lims.exceptions import LimsError, MissingUDFsError

from cg_lims.get.artifacts import get_artifacts, get_qc_output_artifacts
from cg_lims.get.udfs import get_udf_type
from cg_lims import options

import logging
import sys

import click

from cg_lims import options
from cg_lims.exceptions import LimsError, MissingUDFsError
from cg_lims.get.artifacts import get_artifacts

LOG = logging.getLogger(__name__)


def find_reads_to_sequence(process: Process, lims: Lims) -> Tuple[int, int]:
    """Function to copy Missing reads Pool (M) from input artifact if existing,
     otherwise Reads missing (M) from sample."""
    
    failed_artifacts = 0
    passed_artifacts = 0

    for input, output in process.input_output_maps:
        if output.get('output-type') != 'Analyte':
            continue

        input_artifact = Artifact(lims, id=input['limsid'])
        output_artifact = Artifact(lims, id=output['limsid'])
        if input_artifact.udf.get('Missing reads Pool (M)') is not None:
            reads_to_sequence = input_artifact.udf.get('Missing reads Pool (M)')
        elif output_artifact.samples[0].udf.get('Reads missing (M)') is not None:
            reads_to_sequence = output_artifact.samples[0].udf.get('Reads missing (M)')
        else:
            failed_artifacts +=1
            continue

        output_artifact.udf['Reads to sequence (M)'] = str(reads_to_sequence)
        output_artifact.put()
        passed_artifacts += 1
    return passed_artifacts, failed_artifacts



@click.command()
@click.pass_context
def reads_to_sequence(ctx):
    """Script to find Reads to sequence (M) for a sample or a pool"""

    process = ctx.obj["process"]
    lims = ctx.obj["lims"]

    try:
        find_reads_to_sequence(process=process, lims=lims)
        click.echo("Udfs have been set on all samples.")
    except LimsError as e:
        sys.exit(e.message)
