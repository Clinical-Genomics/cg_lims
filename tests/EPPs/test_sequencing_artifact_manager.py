from genologics.entities import Artifact, Process
from cg_lims.EPPs.qc.sequencing_quality_checker import SequencingArtifactManager


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
