from genologics.entities import Artifact, Process
from cg_lims.EPPs.qc.sequencing_artifact_manager import (
    Q30_FIELD,
    QUALITY_CHECK_FAILED,
    READS_FIELD,
    SequencingArtifactManager,
)


def test_get_flow_cell_name(lims_process_with_novaseq_data: Process):
    # GIVEN a sequencing artifact manager
    artifact_manager = SequencingArtifactManager(lims_process_with_novaseq_data)

    # WHEN extracting the flow cell name
    flow_cell_name: str = artifact_manager.get_flow_cell_name()

    # THEN the flow cell name should have been set
    assert isinstance(flow_cell_name, str)
    assert flow_cell_name is not ""


def test_get_q30_threshold(lims_process_with_novaseq_data: Process):
    # GIVEN a sequencing artifact manager
    artifact_manager = SequencingArtifactManager(lims_process_with_novaseq_data)

    # WHEN extracting the q30 threshold
    q30_threshold: int = artifact_manager.get_q30_threshold()

    # THEN the q30 threshold should have been set
    assert isinstance(q30_threshold, int)
    assert q30_threshold is not 0


def test_sample_artifacts_initialization(lims_process_with_novaseq_data: Process):
    """Test that the internal data structure holding the sample artifacts is populated."""
    # GIVEN a lims mock process
    # WHEN the manager is instantiated
    artifact_manager = SequencingArtifactManager(lims_process_with_novaseq_data)

    # THEN the internal dictionary of sample artifacts was populated
    assert artifact_manager.sample_artifacts is not {}

    # THEN each entry is a key value pair of the sample id and a dictionary of a lane and artifact
    for (
        sample_id,
        lane_artifact_dict,
    ) in artifact_manager.sample_artifacts.items():
        assert isinstance(sample_id, str)
        assert isinstance(lane_artifact_dict, dict)

        for lane, artifact in lane_artifact_dict.items():
            assert isinstance(lane, int)
            assert isinstance(artifact, Artifact)


def test_updating_samples(lims_process_with_novaseq_data: Process):
    # GIVEN a sequencing artifact manager
    artifact_manager = SequencingArtifactManager(lims_process_with_novaseq_data)

    # GIVEN a list of the sample ids and lanes
    sample_lane_pairs = [
        (sample_id, lane)
        for sample_id in artifact_manager.sample_artifacts
        for lane in artifact_manager.sample_artifacts[sample_id]
    ]

    # WHEN updating the sample artifacts
    for sample_id, lane in sample_lane_pairs:
        artifact_manager.update_sample(
            sample_lims_id=sample_id,
            lane=lane,
            reads=0,
            q30_score=0,
            passed_quality_control=False,
        )

    # THEN the sample artifacts should have been updated
    for sample_id, lane in sample_lane_pairs:
        sample_artifact = artifact_manager._get_sample_artifact(
            sample_lims_id=sample_id, lane=lane
        )
        assert sample_artifact is not None
        assert sample_artifact.udf[Q30_FIELD] == 0
        assert sample_artifact.udf[READS_FIELD] == 0
        assert sample_artifact.qc_flag == QUALITY_CHECK_FAILED
