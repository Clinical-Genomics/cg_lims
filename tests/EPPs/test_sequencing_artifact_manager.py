from genologics.entities import Process
from genologics.lims import Lims
from cg_lims.EPPs.qc.sequencing_artifact_manager import (
    SampleArtifacts,
    SequencingArtifactManager,
)
from cg_lims.get.artifacts import get_lane_sample_artifacts
from cg_lims.get.fields import get_artifact_lims_id
from cg_lims.set.qc import QualityCheck
from cg_lims.set.udfs import UserDefinedFields


def test_sample_artifacts_add_and_get(lims_process_with_novaseq_data: Process):
    # GIVEN all sample artifacts mapped to their lanes in the process
    lane_samples = get_lane_sample_artifacts(lims_process_with_novaseq_data)
    assert lane_samples

    # GIVEN a sample artifacts object
    sample_artifacts: SampleArtifacts = SampleArtifacts()

    # WHEN populating the sample artifacts
    for lane, artifact in lane_samples:
        sample_id: str = get_artifact_lims_id(artifact)
        sample_artifacts.add(artifact=artifact, lane=lane, sample_id=sample_id)

    # THEN all the artifacts should be retrievable
    for lane, artifact in lane_samples:
        sample_lims_id = get_artifact_lims_id(artifact)
        assert sample_artifacts.get(sample_lims_id, lane) == artifact


def test_get_flow_cell_name(lims_process_with_novaseq_data: Process, lims: Lims):
    # GIVEN a sequencing artifact manager
    artifact_manager = SequencingArtifactManager(
        process=lims_process_with_novaseq_data, lims=lims
    )

    # WHEN extracting the flow cell name
    flow_cell_name: str = artifact_manager.flow_cell_name

    # THEN the flow cell name should have been set
    assert isinstance(flow_cell_name, str)
    assert flow_cell_name is not ""


def test_get_q30_threshold(lims_process_with_novaseq_data: Process, lims: Lims):
    # GIVEN a sequencing artifact manager
    artifact_manager = SequencingArtifactManager(
        process=lims_process_with_novaseq_data, lims=lims
    )

    # WHEN extracting the q30 threshold
    q30_threshold: int = artifact_manager.q30_threshold

    # THEN the q30 threshold should have been set
    assert isinstance(q30_threshold, int)
    assert q30_threshold is not 0


def test_updating_samples(lims_process_with_novaseq_data: Process, lims: Lims):
    # GIVEN a sequencing artifact manager
    artifact_manager = SequencingArtifactManager(
        process=lims_process_with_novaseq_data, lims=lims
    )

    # GIVEN all sample artifacts mapped to their lanes in the process
    lane_samples = get_lane_sample_artifacts(lims_process_with_novaseq_data)
    assert lane_samples

    # WHEN updating the sample artifacts
    for lane, sample in lane_samples:
        sample_id: str = get_artifact_lims_id(sample)
        artifact_manager.update_sample(
            sample_lims_id=sample_id,
            lane=lane,
            reads=0,
            q30_score=0,
            passed_quality_control=False,
        )

    # THEN the sample artifacts should have been updated
    for lane, sample in lane_samples:
        assert sample is not None
        assert sample.udf[UserDefinedFields.Q30] == 0
        assert sample.udf[UserDefinedFields.READS] == 0
        assert sample.qc_flag == QualityCheck.FAILED
