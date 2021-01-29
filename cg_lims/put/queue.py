import logging
import pathlib
from typing import List

from genologics.config import BASEURI
from genologics.entities import Artifact, Process, Sample
from genologics.lims import Lims

from cg_lims.get.ids import unique_list_of_ids

LOG = logging.getLogger(__name__)

from cg_lims.exceptions import MissingArtifactError, QueueArtifactsError


def queue_artifacts(lims: Lims, artifacts: List[Artifact], workflow_id: str, stage_id: str) -> None:
    """Queue artifacts to stage in workflow."""

    if not artifacts:
        LOG.warning("Failed trying to queue empty list of artifacts.")
        raise MissingArtifactError("No artifacts to queue.")
    stage_uri = f"{BASEURI}/api/v2/configuration/workflows/{workflow_id}/stages/{stage_id}"

    artifact_ids = unique_list_of_ids(artifacts)
    try:
        lims.route_artifacts(artifacts, stage_uri=stage_uri)
        LOG.info(f"Queueing artifacts to {stage_uri}.")
        LOG.info(f"The following artifacts have been queued: {' ,'.join(artifact_ids)}")
    except:
        raise QueueArtifactsError("Failed to queue artifacts.")
