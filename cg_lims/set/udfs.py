from typing import List

from genologics.entities import Artifact

import logging

LOG = logging.getLogger(__name__)


def copy_udf(
    destination_artifact: Artifact, source_artifact: Artifact, artifact_udfs: List[str]
) -> None:
    """Copying artifact udfs from source artifact to destination artifact.
    Logging missing uds without raising error"""

    artifacts_to_put = False

    for udf in artifact_udfs:
        if not source_artifact.udf.get(udf):
            message = f"artifact udf {udf} missing on artifact {source_artifact.id}"
            LOG.error(message)
            continue
        destination_artifact.udf[udf] = source_artifact.udf[udf]
        artifacts_to_put = True

    if artifacts_to_put:
        destination_artifact.put()
