from cg_lims.exceptions import FailingQCError, MissingUDFsError, MissingSampleError
from genologics.entities import Artifact, Sample
from cg_lims.EPPs.udf.calculate.twist_qc_amount import calculate_amount_and_set_qc

import pytest


@pytest.mark.parametrize("volume,concentration,source",
                         [(3, 1, "blood"), (10, 0.1, "cfDNA"), (50, 300, "blood"), (300, 2, "blood"),
                          (10, 10, "blood")])
def test_calculate_amount_and_set_qc_failing(volume, concentration, source, server_flat_tests, artifact_1,
                                             sample_1):
    # GIVEN: A sample with udf Source: <source>,
    # and a related Artifact with udfs: Concentration: <concentration> and  Volume (ul): <volume>

    artifact_1.udf["Volume (ul)"] = volume
    artifact_1.udf["Concentration"] = concentration
    artifact_1.qc_flag == "UNKNOWN"
    artifact_1.put()

    sample_1.udf["Source"] = source
    sample_1.put()

    # THEN FailingQCError is being raised and the artifacts should be FAILED
    with pytest.raises(FailingQCError):
        calculate_amount_and_set_qc(artifacts=[artifact_1])
    assert artifact_1.qc_flag == "FAILED"


@pytest.mark.parametrize("volume,concentration,source", [(35, 10, "cfDNA"), (50, 50, "blood")])
def test_calculate_amount_and_set_qc_passing(volume, concentration, source, server_flat_tests, artifact_1, sample_1):
    # GIVEN: A sample with udf Source: <source>,
    # and a related Artifact with udfs: Concentration: <concentration> and  Volume (ul): <volume>

    artifact_1.udf["Volume (ul)"] = volume
    artifact_1.udf["Concentration"] = concentration
    artifact_1.qc_flag == "UNKNOWN"
    artifact_1.put()
    print(source)
    sample_1.udf["Source"] = source
    sample_1.put()

    # WHEN running calculate_amount_and_set_qc
    calculate_amount_and_set_qc(artifacts=[artifact_1])
    
    # THEN the artifacts should be PASSED
    assert artifact_1.qc_flag == "PASSED"



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
