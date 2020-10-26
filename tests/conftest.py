import pytest
from genologics_mock.lims import MockLims
from genologics_mock.entities import MockArtifact, MockProcess, MockProcessType, MockSample



@pytest.fixture
def config():
    """Get file path to invalid csv"""

    return "tests/fixtures/config.yaml"


@pytest.fixture
def lims():
    return MockLims()


@pytest.fixture
def lims_with_data():
    process_type = MockProcessType(name='SomeTypeOfProcess')
    process_1 = MockProcess(process_type=process_type, date_run='2019-01-01')
    process_2 = MockProcess(process_type=process_type, date_run='2020-01-01')
    sample = MockSample(sample_id='some_sample_id')
    artifact1 = MockArtifact(samples=[sample], parent_process=process_1, type='Analyte')
    artifact2 = MockArtifact(samples=[sample], parent_process=process_2, type= 'Analyte')
    lims = MockLims()
    lims.artifacts = [artifact1, artifact2]
    return lims