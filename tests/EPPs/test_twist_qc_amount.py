from cg_lims.exceptions import FailingQCError, MissingUDFsError, MissingSampleError
from genologics.entities import Artifact, Sample
from cg_lims.EPPs.udf.calculate.twist_qc_amount import calculate_amount_and_set_qc

import pytest


def test_calculate_amount_and_set_qc(server_flat_tests, lims):
    # GIVEN: A list of  artifacts as below

    a1 = Artifact(lims, id='1')
    a1.udf["Volume (ul)"] = 35
    a1.udf["Concentration"] = 10
    a1.put()
    a2 = Artifact(lims, id='2')
    a2.udf["Volume (ul)"] = 3
    a2.udf["Concentration"] = 1
    a2.put()
    a3 = Artifact(lims, id='3')
    a3.udf["Volume (ul)"] = 10
    a3.udf["Concentration"] = 0.1
    a3.put()
    a4 = Artifact(lims, id='4')
    a4.udf["Volume (ul)"] = 50
    a4.udf["Concentration"] = 300
    a4.put()
    a5 = Artifact(lims, id='5')
    a5.udf["Volume (ul)"] = 300
    a5.udf["Concentration"] = 2
    a5.put()
    a6 = Artifact(lims, id='6')
    a6.udf["Volume (ul)"] = 10
    a6.udf["Concentration"] = 10
    a6.put()
    a7 = Artifact(lims, id='7')
    a7.udf["Volume (ul)"] = 50
    a7.udf["Concentration"] = 50
    a7.put()

    sample = Sample(lims, id='S1')
    sample.udf["Source"] = "blood"
    sample.put()

    artifacts=[a1, a2,a3,a4,a5,a6,a7]

    # WHEN running calculate_amount_and_set_qc
    # THEN FailingQCError is being raised and the artifacts should get the expected qc flags
    with pytest.raises(FailingQCError):
        calculate_amount_and_set_qc(artifacts=artifacts)
    assert a1.qc_flag == "PASSED"
    assert a2.qc_flag == "FAILED"
    assert a3.qc_flag == "FAILED"
    assert a4.qc_flag == "FAILED"
    assert a5.qc_flag == "FAILED"
    assert a6.qc_flag == "FAILED"
    assert a7.qc_flag == "PASSED"


def test_calculate_amount_and_set_qc_missing_udf(server_flat_tests, lims):
    # GIVEN: A list of two artifacts with missing udfs

    a1 = Artifact(lims, id='1')
    a1.udf["Volume (ul)"] = 35
    a1.put()
    a2 = Artifact(lims, id='2')
    a2.udf["Concentration"] = 1
    a2.put()

    artifacts = [a1, a2]

    # WHEN running calculate_amount_and_set_qc
    # THEN MissingUDFsError is being raised
    with pytest.raises(MissingUDFsError):
        calculate_amount_and_set_qc(artifacts=artifacts)
