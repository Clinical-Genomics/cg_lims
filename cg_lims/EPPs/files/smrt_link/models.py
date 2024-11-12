import logging
from typing import Optional

from cg_lims.enums import IntEnum, StrEnum
from genologics.lims import Artifact, Process

LOG = logging.getLogger(__name__)


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
