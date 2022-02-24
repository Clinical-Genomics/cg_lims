from typing import List

from genologics.entities import Artifact

import logging

LOG = logging.getLogger(__name__)


def copy_udf(destination_artifact: Artifact, source_artifact: Artifact, artifact_udfs: List[str]):
    """Copying artifact udfs from source artifact to destination artifact.
    Logging missing uds without raising error"""

    for udf in artifact_udfs:
        if not source_artifact.udf.get(udf):
            message = f"artifact udf {udf} missing on artifact {source_artifact.id}"
            LOG.error(message)
            continue
        destination_artifact.udf[udf] = source_artifact.udf.get(udf)
    destination_artifact.put()
