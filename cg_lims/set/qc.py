from typing import Literal
from genologics.entities import Artifact
from enum import Enum


class QualityCheck(str, Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"


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


def set_quality_check_flag(quality_check_passed: bool, artifact: Artifact) -> None:
    qc_flag: str = _get_quality_check_flag(quality_check_passed)
    artifact.qc_flag = qc_flag


def _get_quality_check_flag(quality_check_passed: bool) -> str:
    return QualityCheck.PASSED.value if quality_check_passed else QualityCheck.FAILED.value
