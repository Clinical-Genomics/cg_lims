from typing import Optional

from genologics.entities import Artifact

from cg_lims.exceptions import ArgumentError


def set_qc_fail(
    artifact: Artifact,
    value: float,
    upper_threshold: Optional[float],
    lower_threshold: Optional[float],
) -> None:
    if not upper_threshold or lower_threshold:
        raise ArgumentError(message="Need upper_threshold or lower_threshold to set qc")
    if value >= upper_threshold or value <= lower_threshold:
        artifact.qc_flag = "FAILED"
        artifact.put()
