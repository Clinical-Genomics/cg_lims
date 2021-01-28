import pytest

from cg_lims.EPPs.udf.calculate.twist_qc_amount import calculate_amount_and_set_qc
from cg_lims.exceptions import FailingQCError, MissingSampleError, MissingUDFsError


def test_calculate_amount_and_set_qc(lims, helpers):
    # GIVEN: A list of  artifacts as below

    artifacts_data = [
        {
            "samples": [{"udf": {"Source": "cfDNA"}}],
            "udf": {"Volume (ul)": 35, "Concentration": 10},
        },
        {
            "samples": [{"udf": {"Source": "blood"}}],
            "udf": {"Volume (ul)": 3, "Concentration": 1},
        },
        {
            "samples": [{"udf": {"Source": "cfDNA"}}],
            "udf": {"Volume (ul)": 10, "Concentration": 0.1},
        },
        {
            "samples": [{"udf": {"Source": "blood"}}],
            "udf": {"Volume (ul)": 50, "Concentration": 300},
        },
        {
            "samples": [{"udf": {"Source": "blood"}}],
            "udf": {"Volume (ul)": 300, "Concentration": 2},
        },
        {
            "samples": [{"udf": {"Source": "blood"}}],
            "udf": {"Volume (ul)": 10, "Concentration": 10},
        },
        {
            "samples": [{"udf": {"Source": "blood"}}],
            "udf": {"Volume (ul)": 50, "Concentration": 50},
        },
    ]

    artifacts = helpers.ensure_lims_artifacts(
        lims=lims,
        artifacts_data=artifacts_data,
    )

    # WHEN running calculate_amount_and_set_qc
    # THEN FailingQCError is being raised and the artifacts should get the expected qc flags
    with pytest.raises(FailingQCError):
        calculate_amount_and_set_qc(artifacts=artifacts)
    assert artifacts[0].qc_flag == "PASSED"
    assert artifacts[1].qc_flag == "FAILED"
    assert artifacts[2].qc_flag == "FAILED"
    assert artifacts[3].qc_flag == "FAILED"
    assert artifacts[4].qc_flag == "FAILED"
    assert artifacts[5].qc_flag == "FAILED"
    assert artifacts[6].qc_flag == "PASSED"


def test_calculate_amount_and_set_qc_missing_udf(lims, helpers):
    # GIVEN: A list of two artifacts with missing udfs

    artifacts_data = [
        {
            "samples": [{"udf": {}}],
            "udf": {"Volume (ul)": 35, "Concentration": 10},
        },
        {
            "samples": [{"udf": {"Source": "blood"}}],
            "udf": {"Concentration": 1},
        },
    ]

    artifacts = helpers.ensure_lims_artifacts(
        lims=lims,
        artifacts_data=artifacts_data,
    )

    # WHEN running calculate_amount_and_set_qc
    # THEN MissingUDFsError is being raised
    with pytest.raises(MissingUDFsError):
        calculate_amount_and_set_qc(artifacts=artifacts)


def test_calculate_amount_and_set_qc_missing_samples(lims, helpers):
    # GIVEN: A list of two artifacts with missing udfs

    artifacts_data = [
        {
            "udf": {"Concentration": 10},
        },
        {
            "udf": {"Volume (ul)": 3, "Concentration": 1},
        },
    ]

    artifacts = helpers.ensure_lims_artifacts(
        lims=lims,
        artifacts_data=artifacts_data,
    )

    # WHEN running calculate_amount_and_set_qc
    # THEN MissingSampleError is being raised
    with pytest.raises(MissingSampleError):
        calculate_amount_and_set_qc(artifacts=artifacts)
