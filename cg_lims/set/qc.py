from typing import Literal
from genologics.entities import Artifact


QUALITY_CHECK_PASSED = "PASSED"
QUALITY_CHECK_FAILED = "FAILED"


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
    return QUALITY_CHECK_PASSED if quality_check_passed else QUALITY_CHECK_FAILED
