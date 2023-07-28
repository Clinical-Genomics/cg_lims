from typing import Dict, List
from genologics.entities import Artifact, Process
from genologics.lims import Lims
from cg_lims.EPPs.files.sample_sheet.create_sample_sheet import get_lane_artifacts


from cg_lims.EPPs.qc.sequencing_artifact_manager import SampleArtifacts, SequencingArtifactManager
from cg_lims.get.fields import get_artifact_lims_id
from cg_lims.set.qc import QualityCheck
from cg_lims.set.udfs import Q30_FIELD, READS_FIELD


def test_sample_artifacts_add_and_get(
    lims_process_with_novaseq_data: Process, lims: Lims
):
    # GIVEN all sample artifacts mapped to their lanes in the process
    lane_samples: Dict[int, Artifact] = get_lane_artifacts(lims_process_with_novaseq_data)
    assert lane_samples

    # GIVEN a sample artifacts object
    sample_artifacts: SampleArtifacts = SampleArtifacts()

    # WHEN populating the sample artifacts object
    for lane, artifact in lane_samples.items():
        sample_artifacts.add(artifact=artifact, lane=lane)

    # THEN all the artifacts should be retrievable
    for lane, artifact in lane_samples.items():
        sample_lims_id = get_artifact_lims_id(artifact)
        assert sample_artifacts.get(sample_lims_id, lane)


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

    # GIVEN a list of the sample ids and lanes
    sample_lane_pairs = [
        (sample_id, lane)
        for sample_id in artifact_manager._sample_artifacts
        for lane in artifact_manager._sample_artifacts[sample_id]
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
        assert sample_artifact.qc_flag == QualityCheck.FAILED
