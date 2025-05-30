import logging
import re
from typing import Any, Dict, List, Optional, Pattern

import pandas as pd
from cg_lims.enums import StrEnum
from cg_lims.exceptions import MissingUDFsError
from cg_lims.get.artifacts import get_artifacts, get_non_pooled_artifacts
from cg_lims.get.fields import get_alternative_artifact_well, get_smrtbell_adapter_name
from genologics.lims import Artifact, Container, Process

LOG = logging.getLogger(__name__)


SAMPLE_SETUP_CSV_HEADER: List[str] = [
    "Sample Name",
    "Comment",
    "System Name",
    "Binding Kit",
    "Plate",
    "Well",
    "Number of Samples",
    "Application",
    "Available Starting Sample Volume (uL)",
    "Starting Sample Concentration (ng/uL)",
    "Insert Size (bp)",
    "Control Kit",
    "Cleanup Anticipated Yield (%)",
    "On Plate Loading Concentration (pM)",
    "Cells to Bind (cells)",
    "Prepare Entire Sample",
    "Sequencing Primer",
    "Target Annealing Sample Concentration (nM)",
    "Target Annealing Primer Concentration (nM)",
    "Target Binding Concentration (nM)",
    "Target Polymerase Concentration (X)",
    "Binding Time (min)",
    "Cleanup Bead Type",
    "Cleanup Bead Concentration (X)",
    "Minimum Pipetting Volume (uL)",
    "Percent of Annealing Reaction To Use In Binding (%)",
    "AMPure Diluted Bound Complex Volume (uL)",
    "AMPure Diluted Bound Complex Concentration (ng/uL)",
    "AMPure Purified Complex Volume (uL)",
    "AMPure Purified Complex Concentration (ng/uL)",
    "ProNex Diluted Bound Complex Volume (uL)",
    "ProNex Diluted Bound Complex Concentration (ng/uL)",
    "ProNex Purified Complex Volume (uL)",
    "ProNex Purified Complex Concentration (ng/uL)",
    "Requested Cells Alternate (cells)",
    "Requested OPLC Alternate (pM)",
]


PLATE_PART_NUMBERS: Dict[str, str] = {
    "Revio sequencing plate": "102118800",
    "Revio sequencing plate - 1rxn": "102412400",
    "Revio SPRQ sequencing plate": "103496700",
}


POLYMERASE_KITS: Dict[str, str] = {
    "Revio polymerase kit": "Lxxxxx102739100123199",
    "Revio SPRQ polymerase kit": "Lxxxxx103496900123199",
}


class RevioIndexSets(StrEnum):
    SMRTBELL_INDEX_SET: str = "43f950a9-8bde-3855-6b25-c13368069745"


class RunDesignHeader(StrEnum):
    RUN_SETTINGS: str = "[Run Settings]"
    SMRT_CELL_SETTINGS: str = "[SMRT Cell Settings]"
    SAMPLES: str = "[Samples]"


class SampleSetup:
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
        self.sample_name = artifact.samples[0].id
        self.system_name = process.udf.get("Sequencing Instrument")
        self.binding_kit = POLYMERASE_KITS[process.udf.get("Binding Kit")]
        self.number_of_samples = len(artifact.samples)
        self.application = process.udf.get("Revio Application")
        self.available_volume = artifact.udf.get("Volume (ul)")
        self.starting_concentration = artifact.udf.get("Input Concentration (ng/ul)")
        self.size = artifact.udf.get("Size (bp)")
        self.loading_conc = process.udf.get("Loading Concentration (pM)")
        self.number_of_cells_to_load = artifact.udf.get("SMRT Cells to Load")
        self.prepare_entire_sample = False
        self.sequencing_primer = process.udf.get("Sequencing Primer")
        self.minimum_pipetting_volume = 1

    def get_sample_setup_row(self) -> List[str]:
        """Return a list containing row information for a sample."""
        return [
            self.sample_name,
            "",
            self.system_name,
            self.binding_kit,
            "",
            "",
            self.number_of_samples,
            self.application,
            self.available_volume,
            self.starting_concentration,
            self.size,
            "",
            "",
            self.loading_conc,
            self.number_of_samples,
            self.prepare_entire_sample,
            self.sequencing_primer,
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            self.minimum_pipetting_volume,
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ]


def _build_plate_dict(process: Process) -> Dict[Any, Any]:
    """Create a sequencing plate dict containing plate position (int) and Container object, both as keys and values."""
    containers: List[Container] = process.output_containers()
    plate_1: str = process.udf.get("Plate 1")
    plate_2: str = process.udf.get("Plate 2")
    plate_dict: Dict[Any, Any] = {}
    for container in containers:
        if container.name == plate_1:
            plate_dict[1] = container.name
            plate_dict[container.name] = 1
        elif plate_2 and container.name == plate_2:
            plate_dict[2] = container.name
            plate_dict[container.name] = 2
        else:
            raise MissingUDFsError(f"Error: Container {container.name} is missing from run set up.")
    return plate_dict


def _get_smrt_cell_well(pool: Artifact, plate_dict: Dict[Any, Any]) -> str:
    """Return the SMRT Cell well position of a pool."""
    plate: Container = pool.container
    well: str = get_alternative_artifact_well(artifact=pool)
    return f"{plate_dict[plate.name]}_{well}"


def _is_indexed(pool: Artifact) -> bool:
    """Check if the given pool is barcoded or not."""
    input_artifacts: List[Artifact] = pool.input_artifact_list()
    for input_artifact in input_artifacts:
        if input_artifact.reagent_labels:
            return True
    return False


def _trim_unsupported_characters(name: str) -> str:
    """Return a trimmed sample name only containing supported characters"""
    pattern: Pattern[str] = re.compile(r"[^A-Za-z0-9_:\.-]")
    return re.sub(pattern=pattern, repl="_", string=name)


def _create_pool_dict(plate_dict: Dict[Any, Any], process: Process) -> Dict[str, Artifact]:
    """Create a well-sorted dictionary detailing all pool artifacts within the step."""
    pool_dict: Dict[str, Artifact] = {}
    pool_artifacts: List[Artifact] = get_artifacts(process=process)
    for pool in pool_artifacts:
        pool_dict[_get_smrt_cell_well(pool=pool, plate_dict=plate_dict)] = pool
    return dict(sorted(pool_dict.items()))


class RevioRun:
    process_id: Process
    plates: Dict[Any, Any]
    pools: Dict[str, Artifact]
    run_name: str
    instrument_type: str
    plate_1_type: str
    plate_2_type: Optional[str]
    file_version: int = 1
    run_comments: Optional[str]
    adaptive_loading: bool
    base_kinetics: bool
    consensus_mode: str
    data_project: int = 1

    def __init__(self, process: Process):
        self.process = process
        self.plates = _build_plate_dict(process=process)
        self.pools = _create_pool_dict(plate_dict=self.plates, process=process)
        self.run_name = process.udf.get("Run Name")
        self.instrument_type = process.udf.get("Instrument Type")
        self.plate_1_type = process.udf.get("Plate 1 Type")
        self.plate_2_type = process.udf.get("Plate 2 Type")
        self.run_comments = f"Generated by automation in Clarity LIMS step {process.id}"
        self.adaptive_loading = process.udf.get("Adaptive Loading")
        self.base_kinetics = process.udf.get("Include Base Kinetics")
        self.consensus_mode = process.udf.get("Consensus Mode")

    def _create_run_settings(self) -> str:
        """Return the [Run Settings] section of the run design."""
        plate_rows: str = f"Plate 1,{PLATE_PART_NUMBERS[self.plate_1_type]}\n"
        if 2 in self.plates.keys():
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
        for well, pool in self.pools.items():
            if _is_indexed(pool=pool):
                index_set: str = RevioIndexSets.SMRTBELL_INDEX_SET
            else:
                index_set: str = pool.samples[0].id

            df[well] = [
                _trim_unsupported_characters(name=pool.name),
                pool.udf.get("Library Type"),
                pool.udf.get("Revio Application"),
                pool.udf.get("Movie Acquisition Time (hours)"),
                pool.udf.get("Mean Size (bp)"),
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
        for well, pool in self.pools.items():
            artifacts: List[Artifact] = get_non_pooled_artifacts(artifact=pool)
            for artifact in artifacts:
                row = (
                    f"\n{artifact.samples[0].id},"
                    f"{well},"
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
