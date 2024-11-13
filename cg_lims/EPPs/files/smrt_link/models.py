import logging
from typing import List, Optional

from cg_lims.enums import IntEnum, StrEnum
from cg_lims.get.artifacts import get_artifacts
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
