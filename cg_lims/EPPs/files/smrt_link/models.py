import logging
from typing import Dict, List, Optional

import pandas as pd
from cg_lims.enums import StrEnum
from cg_lims.exceptions import MissingUDFsError, MissingValueError
from cg_lims.get.artifacts import get_artifacts, get_non_pooled_artifacts
from cg_lims.get.fields import get_smrtbell_adapter_name
from genologics.lims import Artifact, Container, Process

LOG = logging.getLogger(__name__)

POOLING_CALCULATOR_CSV_HEADER = (
    '"Library Name","Conc. (ng/uL)","Insert size (bp)","Conc. (pM)","Pooling volume (uL)"\n'
)


PLATE_PART_NUMBERS: Dict[str, str] = {
    "Revio sequencing plate": "102118800",
    "Revio sequencing plate - 1rxn": "102412400",
    "Revio SPRQ sequencing plate": "103496700",
}


INDEX_SET_UUID: Dict[str, str] = {
    "SMRTbell adapter indexes": "43f950a9-8bde-3855-6b25-c13368069745"
}


class RunDesignHeader(StrEnum):
    RUN_SETTINGS: str = "[Run Settings]"
    SMRT_CELL_SETTINGS: str = "[SMRT Cell Settings]"
    SAMPLES: str = "[Samples]"


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


def _build_plate_dict(process: Process) -> Dict[int, Container]:
    """Create a sequencing plate dict containing plate position (int) and Container object"""
    containers = process.output_containers()
    plate_1 = process.udf.get("Plate 1")
    plate_2 = process.udf.get("Plate 2")
    dict = {1: "", 2: ""}
    for container in containers:
        if container.name == plate_1:
            dict[1] = container.name
        elif plate_2 and container.name == plate_2:
            dict[2] = container.name
        else:
            raise MissingUDFsError(f"Error: Container {container.name} is missing from run set up.")
    return dict


def _convert_well(well: str) -> str:
    """Convert a well from the format in Clarity LIMS to the one used in SMRT Link. For example: A:1 -> A01"""
    return well.replace(":", "0")


def _get_smrt_cell_well(pool: Artifact, plate_dict: Dict[int, Container]) -> str:
    """Return the SMRT Cell well position of a pool."""
    plate: Container = pool.container
    for position, plate_object in plate_dict.items():
        if plate_object == plate.name:
            plate_position = position
        elif plate_object:
            raise MissingValueError(f"Can't find container {plate.name} in the run!")
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
    plates: Dict[int, Container]
    pools: List[Artifact]
    run_name: str
    instrument_type: str
    plate_1_type: str
    plate_2_type: Optional[str]
    file_version: int = 1
    run_comments: Optional[str]
    movie_acquisition_time: int
    adaptive_loading: bool = True
    base_kinetics: bool = False
    consensus_mode: bool = True
    data_project: int = 1

    def __init__(self, process: Process):
        self.process: Process = process
        self.plates: Dict[int, Container] = _build_plate_dict(process=process)
        self.pools: List[Artifact] = get_artifacts(process=process)
        self.run_name: str = process.udf.get("Run Name")
        self.instrument_type: str = process.udf.get("Instrument Type")
        self.run_comments: str = (
            f"Generated by automation in https://cg-lims-stage.sys.scilifelab.se/clarity/work-details/{process.id.split('-')[1]}"
        )
        self.movie_acquisition_time: str = process.udf.get("Movie Acquisition Time (hours)")
        self.adaptive_loading: bool = process.udf.get("Adaptive Loading")
        self.base_kinetics: bool = process.udf.get("Include Base Kinetics")
        self.consensus_mode: bool = process.udf.get("Consensus Mode")
        self.plate_1_type: str = process.udf.get("Plate 1 Type")
        self.plate_2_type: str = process.udf.get("Plate 2 Type")

    def _create_run_settings(self) -> str:
        """Return the [Run Settings] section of the run design."""
        plate_rows: str = f"Plate 1,{PLATE_PART_NUMBERS[self.plate_1_type]}\n"
        if self.plates[2]:
            plate_rows += f"Plate 2,{PLATE_PART_NUMBERS[self.plate_2_type]}\n"
        return (
            f"{RunDesignHeader.RUN_SETTINGS}\n"
            f"Instrument Type,{self.instrument_type}\n"
            f"Run Name,{self.run_name}\n"
            f"Run Comments,{self.run_comments}\n"
            f"{plate_rows}"
            f"CSV Version,{self.file_version}\n"
        )

    def _create_smrt_cell_settings(self) -> str:
        """Return the [SMRT Cell Settings] section of the run design."""
        df: pd.DataFrame = pd.DataFrame(
            {
                RunDesignHeader.SMRT_CELL_SETTINGS: [
                    "Well Name",
                    "Library Type",
                    "Application",
                    "Polymerase Kit",
                    "Movie Acquisition Time (hours)",
                    "Insert Size (bp)",
                    "Library Concentration (pM)",
                    "Use Adaptive Loading",
                    "Include Base Kinetics",
                    "Consensus Mode",
                    "Sample is indexed",
                    "Indexes",
                    "Assign Data To Project",
                ]
            }
        )
        for pool in self.pools:
            well: str = _get_smrt_cell_well(pool=pool, plate_dict=self.plates)
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
        return df.to_csv(index=False)

    def _get_sample_settings(self) -> str:
        """Return the [SMRT Cell Settings] section of the run design."""
        section = f"Bio Sample Name,Plate Well,Adapter,Adapter2"
        for pool in self.pools:
            artifacts: List[Artifact] = get_non_pooled_artifacts(artifact=pool)
            for artifact in artifacts:
                row = (
                    f"\n{artifact.samples[0].id},"
                    f"{_get_smrt_cell_well(pool=pool, plate_dict=self.plates)},"
                    f"{get_smrtbell_adapter_name(artifact=artifact)},"
                    f"{get_smrtbell_adapter_name(artifact=artifact)}"
                )
                section += row
        return RunDesignHeader.SAMPLES + "\n" + section + "\n"

    def create_csv(self) -> str:
        """Return the Run Design CSV of a step."""
        return (
            self._create_run_settings()
            + "\n"
            + self._create_smrt_cell_settings()
            + "\n"
            + self._get_sample_settings()
        )
