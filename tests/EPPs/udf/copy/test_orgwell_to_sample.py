import pytest
import random

from genologics.entities import Artifact, Process
from cg_lims.exceptions import MissingUDFsError, MissingCgFieldError
from cg_lims.EPPs.udf.copy.orgwell_to_sample import orgwell_to_sample
from cg_lims.set.udfs import copy_artifact_to_artifact
from tests.conftest import server
from cg_lims.get.artifacts import get_artifacts


# test_samples_with_parent(): Get correct error message.
# test_missing_art_udf(): Missing position or container name.
# test_requeued_samples(): Test what would happen if sample was requeued.
# First test, test that it can do what is buildt to do, assign correct position

def test_assign_correct(lims):
    # GIVEN artifacts with container, random well position and without parent steps.
    udfs = list(['Original Well', 'Original Container'])
    server("calculate_average_size_and_set_qc")
    process = Process(lims, id='24-297378')
    artifacts = get_artifacts(process=process)
    
    rows = [chr(nr) for nr in range(65, 73)]
    for artifact in artifacts:
        random_row = rows[random.randrange(len(rows))]
        random_position = f"{random_row}:{random.randrange(1, 13)}"
        random_container = f"Container {rows[random.randrange(len(rows))]}"

        artifact.location[1] = random_position
        artifact.location[0].name = random_container

        artifact.put()



        
        

    # When running function artifacts_to_sample.
    orgwell_to_sample( artifacts, udfs)
    # THEN the corresponding sample will have the matching qc_flag.
    for artifact in artifacts:
        sample = artifact.samples[0]

        assert sample.udf['Original Well'] == artifact.location[1]
        assert sample.udf['Original Container'] == artifact.location[0].name



def test_correct(lims):
    # GIVEN a list with artifacts without parentsteps with container, random well position and without parent steps.
    Name_Artifacts = ["ACC8653A1PA1","ACC8653A9PA1","ACC8653A17PA1","ACC8653A25PA1"]



    # When running function artifacts_to_sample.

    # THEN the corresponding sample will have the matching qc_flag.




# _____________
# def test_udf_Passed_Initial_QC(lims):
#     # GIVEN every other artifacts have True or False on udf: Passed Initial QC.
#     udf = "Passed Initial QC"
#     server("calculate_average_size_and_set_qc")
#     process = Process(lims, id='24-297378')
#     artifacts = get_artifacts(process=process)
    
#     odd_or_even = 0 
#     for artifact in artifacts:
#         if int(odd_or_even % 2) == 0:
#             artifact.qc_flag = "PASSED"

#         else:
#             artifact.qc_flag = "FAILED"
        
#         artifact.put()
#         odd_or_even += 1

#     # When running function artifacts_to_sample.

#     # THEN the corresponding sample will have the matching qc_flag.
#     for artifact in artifacts:
#         sample = artifact.samples[0]
#         if artifact.qc_flag == 'PASSED':
#             assert sample.udf[udf] == 'True'

#         elif artifact.qc_flag == 'FAILED':
#             assert sample.udf[udf] == 'False'

