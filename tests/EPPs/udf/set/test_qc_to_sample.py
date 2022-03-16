import pytest
from genologics.entities import Artifact, Process

from cg_lims.exceptions import MissingUDFsError, MissingCgFieldError
from cg_lims.EPPs.udf.copy.qc_to_sample import artifacts_to_sample
from cg_lims.set.udfs import copy_artifact_to_artifact
from tests.conftest import server

from cg_lims.get.artifacts import get_artifacts


def test_udf_Passed_Initial_QC(lims):
    # GIVEN every other artifacts have True or False on udf: Passed Initial QC.
    udf = "Passed Initial QC"
    server("calculate_average_size_and_set_qc")
    process = Process(lims, id='24-297378')
    artifacts = get_artifacts(process=process)
    
    odd_or_even = 0 
    for artifact in artifacts:
        if int(odd_or_even % 2) == 0:
            artifact.qc_flag = "PASSED"

        else:
            artifact.qc_flag = "FAILED"
        
        artifact.put()
        odd_or_even += 1

    # When running function artifacts_to_sample.
    artifacts_to_sample(artifacts, udf)

    # THEN the corresponding sample will have the matching qc_flag.
    for artifact in artifacts:
        sample = artifact.samples[0]
        if artifact.qc_flag == 'PASSED':
            assert sample.udf[udf] == 'True'

        elif artifact.qc_flag == 'FAILED':
            assert sample.udf[udf] == 'False'


def test_udf_Passed_Library_QC(lims):
    # GIVEN every other artifacts have True or False on udf: Passed Library QC.
    udf = "Passed Library QC"
    server("calculate_average_size_and_set_qc")
    process = Process(lims, id='24-297378')
    artifacts = get_artifacts(process=process)

    odd_or_even = 0 
    for artifact in artifacts:
        if int(odd_or_even % 2) == 0:
            artifact.qc_flag = "PASSED"

        else:
            artifact.qc_flag = "FAILED"
        
        artifact.put()
        odd_or_even += 1

    # When running function artifacts_to_sample.
    artifacts_to_sample(artifacts, udf)

    # THEN the corresponding sample will have the matching qc_flag.
    for artifact in artifacts:
        sample = artifact.samples[0]
        if artifact.qc_flag == 'PASSED':
            assert sample.udf[udf] == 'True'

        elif artifact.qc_flag == 'FAILED':
            assert sample.udf[udf] == 'False'


def test_change_value(lims):
    # GIVEN sample already has a value on Udfs "Passed Library QC" and "Passed Initial QC".
    server("calculate_average_size_and_set_qc")
    process = Process(lims, id='24-297378')
    artifacts = get_artifacts(process=process)

    odd_or_even = 0 
    for artifact in artifacts:
        if int(odd_or_even % 2) == 0:
            artifact.qc_flag = "PASSED"

        else:
            artifact.qc_flag = "FAILED"
        
        artifact.put()
        odd_or_even += 1    

    udfs = ["Passed Library QC", "Passed Initial QC"]
    for udf in udfs:
        artifacts_to_sample(artifacts, udf)

    # WHEN running function artifacts_to_sample with artifacts with new updated qc_flag values.
    # This for-loop will change all qc_flags (e.g. if previous qc_flag value was True then the new is False).
    odd_or_even = 0 
    for artifact in artifacts:
        if int(odd_or_even % 2) == 0:
            artifact.qc_flag = "FAILED"

        else:
            artifact.qc_flag = "PASSED"
        
        artifact.put()
        odd_or_even += 1    

    udfs = ["Passed Library QC", "Passed Initial QC"]
    for udf in udfs:
        artifacts_to_sample(artifacts, udf)

    # THEN sample should change from old to new value.
    udfs = ["Passed Library QC", "Passed Initial QC"]
    for udf in udfs:
        for artifact in artifacts:
            sample = artifact.samples[0]
            if artifact.qc_flag == 'PASSED':
                assert sample.udf[udf] == 'True'

            elif artifact.qc_flag == 'FAILED':
                assert sample.udf[udf] == 'False' 


def test_pool(lims):
    # GIVEN pools and that every other pool have True or False on udf: Passed Library QC.
    udf = "Passed Library QC"
    server("missing_reads_pool")
    process = Process(lims, id="24-196210")
    artifacts = get_artifacts(process=process, input = True)

    odd_or_even = 0 
    for artifact in artifacts:
        if int(odd_or_even % 2) == 0:
            artifact.qc_flag = "PASSED"

        else:
            artifact.qc_flag = "FAILED"
        
        artifact.put()
        odd_or_even += 1

    # WHEN running function artifacts_to_sample.
    artifacts_to_sample(artifacts, udf)

    # THEN the corresponding sample will have the matching qc_flag
    for artifact in artifacts:
        sample = artifact.samples[0]
        if artifact.qc_flag == 'PASSED':
            assert sample.udf[udf] == 'True'
        elif artifact.qc_flag == 'FAILED':
            assert sample.udf[udf] == 'False'


def test_unknown_qc_flag(lims):
    # GIVEN samples with unknown qc_flag value.
    udf = "Passed Library QC"
    server("calculate_average_size_and_set_qc")
    process = Process(lims, id='24-297378')
    artifacts = get_artifacts(process=process, input = True)

    # WHEN running function artifacts_to_sample.
    # THEN MissingUDFsERROR should be raised.
    with pytest.raises(MissingUDFsError) as error_message:
        artifacts_to_sample(artifacts, udf)
