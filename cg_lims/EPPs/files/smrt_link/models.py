import logging
from typing import List, Optional

import pandas as pd
from cg_lims.enums import IntEnum, StrEnum
from cg_lims.get.artifacts import get_artifacts, get_non_pooled_artifacts
from cg_lims.get.fields import get_smrtbell_adapter_name
from genologics.lims import Artifact, Process

LOG = logging.getLogger(__name__)

POOLING_CALCULATOR_CSV_HEADER = (
    '"Library Name","Conc. (ng/uL)","Insert size (bp)","Conc. (pM)","Pooling volume (uL)"\n'
)


class SampleSetupObject:
    sample_name: str
    system_name: str
    binding_kit: str
    number_of_samples: int
    application: str
    available_volume: float
    starting_concentration: float
    size: int
    loading_conc: float
    number_of_cells_to_load: int
    prepare_entire_sample: bool
    sequencing_primer: str
    minimum_pipetting_volume: float

    def __init__(self, artifact: Artifact):
        process = artifact.parent_process
        self.sample_name: str = artifact.samples[0].id
        self.system_name: str = process.udf.get("Sequencing Instrument")
        self.binding_kit: str = process.udf.get("Binding Kit")
        self.number_of_samples = len(artifact.samples)
        self.application: str = process.udf.get("Prep Type")
        self.available_volume: float = artifact.udf.get("Volume (ul)")
        self.starting_concentration: float = artifact.udf.get("Input Concentration (ng/ul)")
        self.size: int = artifact.udf.get("Size (bp)")
        self.loading_conc: float = process.udf.get("Loading Concentration (pM)")
        self.number_of_cells_to_load: int = artifact.udf.get("SMRT Cells to Load")
        self.prepare_entire_sample: bool = False
        self.sequencing_primer: str = process.udf.get("Sequencing Primer")
        self.minimum_pipetting_volume: float = 1

    def get_sample_setup_row(self):
        return (
            f'"{self.sample_name}",'
            f'"",'
            f'"{self.system_name}",'
            f'"{self.binding_kit}",'
            f'"",'
            f'"",'
            f'"{self.number_of_samples}",'
            f'"{self.application}",'
            f'"{self.available_volume}",'
            f'"{self.starting_concentration}",'
            f'"{self.size}",'
            f'"",'
            f'"",'
            f'"{self.loading_conc}",'
            f'"{self.number_of_samples}",'
            f'"{self.prepare_entire_sample}",'
            f'"{self.sequencing_primer}",'
            f'"",'
            f'"",'
            f'"",'
            f'"",'
            f'"",'
            f'"",'
            f'"",'
            f'"{self.minimum_pipetting_volume}",'
            f'"",'
            f'"",'
            f'"",'
            f'"",'
            f'"",'
            f'"",'
            f'"",'
            f'"",'
            f'"",'
            f'"",'
            f'""'
        )


def _build_pooling_sample_row(input_artifact: Artifact):
    return (
        f'"{input_artifact.samples[0].id}",'
        f'"{input_artifact.udf.get("Concentration (ng/ul)")}",'
        f'"{input_artifact.udf.get("Size (bp)")}",'
        f'"",'
        f'""'
    )


class PoolingCalculator:
    pool_artifact: Artifact
    number_of_samples: int
    pool_volume: float
    concentration_unit: str
    target_concentration: float

    def __init__(self, pool_artifact: Artifact):
        parent_process: Process = pool_artifact.parent_process
        self.pool_artifact: Artifact = pool_artifact
        self.number_of_samples: int = len(pool_artifact.samples)
        self.pool_volume: str = parent_process.udf.get("Pool Volume (ul)")
        self.concentration_unit: str = "(pM)"
        self.target_concentration: str = parent_process.udf.get("Target Pool Concentration (pM)")

    def _build_sample_section(self):
        section = ""
        for input_artifact in self.pool_artifact.input_artifact_list():
            section += _build_pooling_sample_row(input_artifact=input_artifact) + "\n"
        return section

    def _build_footer(self):
        return f'"# n: {self.number_of_samples} volume: {self.pool_volume} units: {self.concentration_unit} conc: {self.target_concentration} buffer:","","","",""'

    def build_csv(self):
        return POOLING_CALCULATOR_CSV_HEADER + self._build_sample_section() + self._build_footer()


class RunDesignHeader(StrEnum):
    RUN_SETTINGS: str = "[Run Settings]"
    SMRT_CELL_SETTINGS: str = "[SMRT Cell Settings]"
    SAMPLES: str = "[Samples]"


def _convert_well(well: str) -> str:
    """Convert a well from the format in Clarity LIMS to the one used in SMRT Link. For example: A:1 -> A01"""
    return well.replace(":", "0")


def _get_smrt_cell_well(pool: Artifact) -> str:
    """Return the SMRT Cell well position of a pool."""
    plate_position: str = pool.container.udf["Plate Position"]
    well: str = _convert_well(well=pool.location[1])
    return f"{plate_position}_{well}"


def _is_indexed(pool: Artifact) -> bool:
    """Check if the given pool is barcoded or not."""
    input_artifacts: List[Artifact] = pool.input_artifact_list()
    for input_artifact in input_artifacts:
        if input_artifact.reagent_labels:
            return True
    return False


class RevioRun:
    process_id: Process
    pools: List[Artifact]
    run_name: str
    instrument_type: str
    plate_1: str
    plate_2: Optional[str]
    file_version: int = 1
    run_comments: Optional[str]
    movie_acquisition_time: int
    adaptive_loading: bool = True
    base_kinetics: bool = False
    consensus_mode: bool = True
    data_project: int = 1

    def __init__(self, process: Process):
        self.process: Process = process
        self.pools: get_artifacts(process=process)
        self.run_name: str = process.udf.get("Run Name")
        self.instrument_type: str = process.udf.get("Instrument Type")
        self.plate_1: str = "test"
        self.plate_2: str = "test"
        self.run_comments: str = "Generated by automation in cg-lims.sys.scilifelab.se"
        self.movie_acquisition_time: str = process.udf.get("Movie Acquisition Time (hours)")
        self.adaptive_loading: bool = process.udf.get("Adaptive Loading")
        self.base_kinetics: bool = process.udf.get("Include Base Kinetics")
        self.consensus_mode: bool = process.udf.get("Consensus Mode")

    def _create_run_settings(self) -> str:
        """Return the [Run Settings] section of the run design."""
        return (
            f"{RunDesignHeader.RUN_SETTINGS},\n"
            f"Instrument Type,{self.instrument_type}\n"
            f"Run Name,{self.run_name}\n"
            f"Run Comments,{self.run_comments}\n"
            f"Plate 1,{self.plate_1}\n"
            f"Plate 2,{self.plate_2}\n"
            f"CSV Version,{self.file_version}\n"
        )

    def _create_smrt_cell_settings(self) -> str:
        """Return the [SMRT Cell Settings] section of the run design."""
        df: pd.DataFrame = pd.DataFrame[
            {
                RunDesignHeader.SMRT_CELL_SETTINGS: [
                    "Well Name",
                    "Library Type",
                    "Application",
                    "Polymerase Kit",
                    "Movie Acquisition Time (hours)",
                    "Insert Size (bp)",
                    "Library Concentration (pM)",
                    "Adaptive Loading",
                    "Include Base Kinetics",
                    "Consensus Mode",
                    "Sample is indexed",
                    "Indexes",
                    "Assign Data To Project",
                ]
            }
        ]
        for pool in self.pools:
            well: str = _get_smrt_cell_well(pool=pool)
            if _is_indexed(pool=pool):
                index_set: str = (
                    "43f950a9-8bde-3855-6b25-c13368069745"  # how do we fetch this one??
                )
            else:
                index_set: str = pool.samples[0].id

            df[well] = [
                pool.name,
                pool.udf.get("Library Type"),
                pool.udf.get("Revio Application"),
                pool.udf.get("Polymerase Kit"),
                self.movie_acquisition_time,
                pool.udf.get("Average Size (bp)"),
                pool.udf.get("Library Concentration (pM)"),
                self.adaptive_loading,
                self.base_kinetics,
                self.consensus_mode,
                _is_indexed(pool=pool),
                index_set,
                self.data_project,
            ]
        return df.to_csv() + "\n"

    def _get_sample_settings(self) -> str:
        """Return the [SMRT Cell Settings] section of the run design."""
        section = f"\nBio Sample Name,Plate Well,Adapter,Adapter2"
        for pool in self.pools:
            artifacts: List[Artifact] = get_non_pooled_artifacts(artifact=pool)
            for artifact in artifacts:
                row = (
                    f"\n{artifact.samples[0].id},"
                    f"{_get_smrt_cell_well(pool=pool)},"
                    f"{get_smrtbell_adapter_name(artifact=artifact)},"
                    f"{get_smrtbell_adapter_name(artifact=artifact)}"
                )
                section += row
        return RunDesignHeader.SAMPLES + "\n" + section + "\n"

    def create_csv(self) -> str:
        """Return the Run Design CSV of a step."""
        return (
            self._create_run_settings()
            + self._create_smrt_cell_settings()
            + self._get_sample_settings()
        )
