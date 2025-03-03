from typing import List, Optional, Set, Tuple

from cg_lims.EPPs.qc.sequencing_artifact_manager import (
    SmrtCellSampleArtifacts,
    SmrtCellSampleManager,
)
from cg_lims.get.artifacts import get_smrt_cell_sample_artifacts
from cg_lims.get.fields import get_artifact_sample_id
from cg_lims.set.qc import QualityCheck
from genologics.entities import Artifact, Process
from genologics.lims import Lims
from tests.conftest import server


def test_smrt_cell_sample_artifacts_add_and_get(lims: Lims):
    server("revio_demux_run")

    # GIVEN all sample artifacts mapped to their SMRT Cells in the process
    process: Process = Process(lims=lims, id="24-558673")
    cell_samples: List[Tuple[str, Artifact]] = get_smrt_cell_sample_artifacts(
        process=process, smrt_cell_udf="SMRT Cell ID"
    )
    assert cell_samples

    # GIVEN a cell sample artifacts object
    cell_sample_artifacts: SmrtCellSampleArtifacts = SmrtCellSampleArtifacts()

    # WHEN populating the cell-sample artifacts
    for smrt_cell_id, artifact in cell_samples:
        sample_id: Optional[str] = get_artifact_sample_id(artifact=artifact)
        cell_sample_artifacts.add(artifact=artifact, sample_id=sample_id, smrt_cell_id=smrt_cell_id)

    # THEN all the artifacts should be retrievable
    for cell, artifact in cell_samples:
        sample_id: str = get_artifact_sample_id(artifact)
        assert cell_sample_artifacts.get(sample_id=sample_id, smrt_cell_id=cell) == artifact


def test_smrt_cell_sample_artifacts_get_cells_and_samples(lims: Lims):
    server("revio_demux_run")

    # GIVEN all sample artifacts mapped to their SMRT Cells in the process
    process: Process = Process(lims=lims, id="24-558673")
    cell_samples: List[Tuple[str, Artifact]] = get_smrt_cell_sample_artifacts(
        process=process, smrt_cell_udf="SMRT Cell ID"
    )
    assert cell_samples

    # GIVEN a populated cell sample artifacts object
    cell_sample_artifacts: SmrtCellSampleArtifacts = SmrtCellSampleArtifacts()
    for smrt_cell_id, artifact in cell_samples:
        sample_id: Optional[str] = get_artifact_sample_id(artifact=artifact)
        cell_sample_artifacts.add(artifact=artifact, sample_id=sample_id, smrt_cell_id=smrt_cell_id)

    # WHEN fetching all cells and samples from the SmrtCellSampleArtifacts object
    cells_set: Set[str] = cell_sample_artifacts.get_cells()
    cell_sample_combinations: Set[Tuple[str, str]] = (
        cell_sample_artifacts.get_cell_sample_combinations()
    )

    # THEN all SMRT Cell IDs and unique cell-sample combinations should be retrieved
    all_cells_in_step: List[str] = []
    all_cell_sample_combinations: List[Tuple[str, str]] = []
    for cell, artifact in cell_samples:
        sample_id: str = get_artifact_sample_id(artifact)
        all_cells_in_step.append(cell)
        all_cell_sample_combinations.append((cell, sample_id))
    assert cells_set == set(all_cells_in_step)
    assert cell_sample_combinations == set(all_cell_sample_combinations)


def test_updating_samples(lims: Lims):
    server("revio_demux_run")

    # GIVEN a PacBio sequencing artifact manager
    process: Process = Process(lims=lims, id="24-558673")
    artifact_manager = SmrtCellSampleManager(process=process, lims=lims)

    # GIVEN all sample artifacts mapped to their SMRT Cells in the process
    cell_samples: List[Tuple[str, Artifact]] = get_smrt_cell_sample_artifacts(
        process=process, smrt_cell_udf="SMRT Cell ID"
    )
    assert cell_samples

    # WHEN updating the cell-sample artifacts
    for cell, artifact in cell_samples:
        sample_id: str = get_artifact_sample_id(artifact)
        artifact_manager.update_sample(
            sample_id=sample_id,
            smrt_cell_id=cell,
            hifi_yield=350000,
            hifi_reads=15000,
            hifi_median_read_quality="Q38",
            hifi_mean_read_length=16000,
            passed_quality_control=False,
        )

    # THEN the artifacts should have been updated
    for cell, artifact in cell_samples:
        assert cell is not None
        assert artifact.udf["HiFi Yield"] == 350000
        assert artifact.udf["HiFi Reads"] == 15000
        assert artifact.udf["HiFi Mean Read Length"] == 16000
        assert artifact.udf["HiFi Median Read Quality"] == "Q38"
        assert artifact.qc_flag == QualityCheck.FAILED
