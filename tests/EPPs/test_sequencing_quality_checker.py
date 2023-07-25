from genologics.entities import Artifact, Process

from cg_lims.EPPs.qc.sequencing_quality_checker import SequencingArtifactManager, SequencingQualityChecker
from cg_lims.status_db_api import StatusDBAPI


def test_get_flow_cell_name(
    lims_process_with_novaseq_data: Process, status_db_api_client: StatusDBAPI
):
    # GIVEN a sequencing artifact manager
    artifact_manager = SequencingArtifactManager(lims_process_with_novaseq_data)

    # GIVEN a sequencing artifact manager
    sequencing_quality_checker: SequencingQualityChecker = SequencingQualityChecker(
        status_db_api=status_db_api_client,
        artifact_manager=artifact_manager
    )
