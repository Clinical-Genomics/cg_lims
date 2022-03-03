from genologics.entities import Process
from cg_lims.EPPs.udf.copy.reads_to_sequence import find_reads_to_sequence
from cg_lims.get.artifacts import get_artifacts
from cg_lims.get.samples import get_process_samples
from tests.conftest import server



def test_find_reads_to_sequence(lims):
    # GIVEN: A process with 5 input artifacts, where one of the input artifacts has the
    # udf 'Missing reads Pool (M)' set to 190.
    # And all the samples have udf 'Reads to sequence (M)' set to 6

    server("find_reads_to_sequence")
    process = Process(lims, id="24-196211")
    output_artifacts = get_artifacts(process=process, input=False)
    for output_artifact in output_artifacts:
        output_artifact.udf.clear()
        output_artifact.put()

    # WHEN running find_reads_to_sequence
    passed_artifacts, failed_artifacts = find_reads_to_sequence(process=process, lims=lims)

    # THEN the output artifact udf 'Reads to sequence (M)' will be fetched from the
    # input artifact udf 'Missing reads Pool (M)' if it exist,
    # oterwise from sample udf 'Reads to sequence (M)'
    assert passed_artifacts == 5
    assert failed_artifacts == 0
    for artifact in output_artifacts:
        if artifact.id == '2-1454725':
            assert artifact.udf['Reads to sequence (M)'] == '190'
        else:
            assert artifact.udf['Reads to sequence (M)'] == '6'


def test_find_reads_to_sequence_missing_udfs(lims):
    # GIVEN: A process with 5 input artifacts, where one of the input artifacts has the
    # udf 'Missing reads Pool (M)' set to 190
    # And no samples have udf 'Reads to sequence (M)' set.

    server("find_reads_to_sequence")
    process = Process(lims, id="24-196211")
    samples=get_process_samples(process=process)
    for sample in samples:
        sample.udf.clear()
        sample.put()

    output_artifacts = get_artifacts(process=process, input=False)

    # WHEN running find_reads_to_sequence
    passed_artifacts, failed_artifacts = find_reads_to_sequence(process=process, lims=lims)

    # THEN the output artifact udf 'Reads to sequence (M)' will be fetched from the
    # input artifact udf 'Missing reads Pool (M)' if it exist,
    # the other artifacts will fail.
    assert passed_artifacts == 1
    assert failed_artifacts == 4
