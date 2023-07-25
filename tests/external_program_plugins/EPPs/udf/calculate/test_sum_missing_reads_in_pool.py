from genologics.entities import Process
from cg_lims.EPPs.udf.calculate.sum_missing_reads_in_pool import sum_reads_in_pool
from cg_lims.get.artifacts import get_artifacts
from tests.conftest import server



def test_sum_reads_pool(lims):
    # GIVEN: A process with pools, where the samples of each pool have the udf 'Reads missing (M)' set.

    server("missing_reads_pool")
    process = Process(lims, id="24-196210")
    artifacts = get_artifacts(process=process, input=False)

    # WHEN running sum_reads_in_pool
    passed_artifacts, failed_artifacts = sum_reads_in_pool(artifacts=artifacts)

    # THEN all pools passed and each pool udf: 'Missing reads Pool (M)' is the sum of ther sample reads.
    assert failed_artifacts == 0
    for artifact in artifacts:
        assert artifact.udf.get('Missing reads Pool (M)') == sum(sample.udf.get("Reads missing (M)") for sample in artifact.samples)



def test_sum_reads_pool_missing_udf(lims):
    # GIVEN: A process with pools, where the samples of each pool have the udf 'Reads missing (M)' set except one.

    server("missing_reads_pool")
    process = Process(lims, id="24-196210")
    artifacts = get_artifacts(process=process, input=False)
    a_sample_in_a_pool = artifacts[0].samples[0]
    a_sample_in_a_pool.udf["Reads missing (M)"] = None
    a_sample_in_a_pool.put()

    # WHEN running sum_reads_in_pool,
    passed_artifacts, failed_artifacts = sum_reads_in_pool(artifacts=artifacts)

    # THEN assert one artifact failed
    assert failed_artifacts == 1
