from genologics.entities import Artifact, Process
from cg_lims.EPPs.qc.sequencing_quality_checker import Q30_FIELD, QUALITY_CHECK_PASSED, READS_FIELD, SequencingArtifactManager


def test_get_flow_cell_name(lims_process_with_novaseq_data: Process):
    # GIVEN a sequencing artifact manager
    sequencing_artifact_manager = SequencingArtifactManager(lims_process_with_novaseq_data)

    # WHEN extracting the flow cell name
    flow_cell_name: str = sequencing_artifact_manager.get_flow_cell_name()

    # THEN the flow cell name should have been set
    assert isinstance(flow_cell_name, str)
    assert flow_cell_name is not ""

def test_get_q30_threshold(lims_process_with_novaseq_data: Process):
    # GIVEN a sequencing artifact manager
    sequencing_artifact_manager = SequencingArtifactManager(lims_process_with_novaseq_data)

    # WHEN extracting the q30 threshold
    q30_threshold: int = sequencing_artifact_manager.get_q30_threshold()

    # THEN the q30 threshold should have been set
    assert isinstance(q30_threshold, int)
    assert q30_threshold is not 0


def test_sample_artifacts_initialization(lims_process_with_novaseq_data: Process):
    """Test that the internal data structure holding the sample artifacts is populated."""
    # GIVEN a lims mock process
    # WHEN the manager is instantiated
    sequencing_artifact_manager = SequencingArtifactManager(lims_process_with_novaseq_data)

    # THEN the internal dictionary of sample artifacts was populated
    assert sequencing_artifact_manager.sample_artifacts is not {}

    # THEN each entry is a key value pair of the sample id and a dictionary of a lane and artifact
    for sample_id, lane_artifact_dict in sequencing_artifact_manager.sample_artifacts.items():
        assert isinstance(sample_id, str)
        assert isinstance(lane_artifact_dict, dict)

        for lane, artifact in lane_artifact_dict.items():
            assert isinstance(lane, int)
            assert isinstance(artifact, Artifact)
