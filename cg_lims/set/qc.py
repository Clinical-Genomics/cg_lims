from typing import Literal
from genologics.entities import Artifact


def set_qc_fail(
    artifact: Artifact,
    value: float,
    threshold: float,
    criteria: Literal[">=", "<=", ">", "<", "==", "!="],
) -> None:
    if criteria == ">=" and value >= threshold:
        artifact.qc_flag = "FAILED"
    elif criteria == "<=" and value <= threshold:
        artifact.qc_flag = "FAILED"
    elif criteria == ">" and value > threshold:
        artifact.qc_flag = "FAILED"
    elif criteria == "<" and value < threshold:
        artifact.qc_flag = "FAILED"
    elif criteria == "==" and value == threshold:
        artifact.qc_flag = "FAILED"
    elif criteria == "!=" and value != threshold:
        artifact.qc_flag = "FAILED"
