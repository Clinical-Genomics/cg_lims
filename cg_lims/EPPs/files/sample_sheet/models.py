from genologics.lims import Process
from typing import Optional
import logging
from enum import Enum

LOG = logging.getLogger(__name__)


class StrEnum(str, Enum):
    def __str__(self) -> str:
        return str.__str__(self)


class IntEnum(int, Enum):
    def __int__(self) -> int:
        return int.__int__(self)


class IndexSetup(IntEnum):
    DUAL_INDEX: int = 2
    SINGLE_INDEX: int = 1


class IndexType(StrEnum):
    INDEX_1: str = "i7"
    INDEX_2: str = "i5"


class SampleSheetHeader(StrEnum):
    FILE_SECTION: str = "[Header]"
    READS_SECTION: str = "[Reads]"
    SETTINGS_SECTION: str = "[Sequencing_Settings]"
    BCL_SETTINGS_SECTION: str = "[BCLConvert_Settings]"
    BCL_DATA_SECTION: str = "[BCLConvert_Data]"


class IlluminaIndex:
    sequence: str
    type: str

    def __init__(self, sequence: str, type: str):
        self.sequence: str = sequence
        self.type: str = type


class NovaSeqXRun:
    process_id: Process
    run_name: str
    file_format: int = 2
    instrument_type: str
    instrument_platform: str
    index_orientation: str
    read_1_cycles: int
    read_2_cycles: Optional[int]
    index_1_cycles: Optional[int]
    index_2_cycles: Optional[int]
    override_cycles: Optional[bool] = True
    bclconvert_software_version: str
    bclconvert_app_version: Optional[str]
    fastq_compression_format: str
    trim_adapters: Optional[bool] = False
    barcode_mismatches: Optional[bool] = True

    def __init__(self, process: Process):
        self.process: Process = process
        self.run_name: str = process.udf.get("Experiment Name")
        self.instrument_type: str = "NovaSeqxPlus"
        self.instrument_platform: str = "NovaSeqXSeries"
        self.index_orientation: str = "Forward"
        self.read_1_cycles: int = process.udf.get("Read 1 Cycles")
        self.read_2_cycles: int = process.udf.get("Read 2 Cycles")
        self.index_1_cycles: int = process.udf.get("Index Read 1")
        self.index_2_cycles: int = process.udf.get("Index Read 2")
        self.bclconvert_software_version: str = process.udf.get("BCLConvert Software Version")
        self.fastq_compression_format: str = process.udf.get("Compression Format")

    def create_head_section(self) -> str:
        """Return the [Head] section of the sample sheet."""
        return (
            f"{SampleSheetHeader.FILE_SECTION},\n"
            f"FileFormatVersion,{self.file_format}\n"
            f"RunName,{self.run_name}\n"
            f"InstrumentType,{self.instrument_type}\n"
            f"InstrumentPlatform,{self.instrument_platform}\n"
            f"IndexOrientation,{self.index_orientation}\n\n"
        )

    def create_reads_section(self) -> str:
        """Return the [Reads] section of the sample sheet."""
        return (
            f"{SampleSheetHeader.READS_SECTION}\n"
            f"Read1Cycles,{self.read_1_cycles}\n"
            f"Read2Cycles,{self.read_2_cycles}\n"
            f"Index1Cycles,{self.index_1_cycles}\n"
            f"Index2Cycles,{self.index_2_cycles}\n\n"
        )

    def get_bcl_data_header_row(self) -> str:
        """Return the .csv-header of the BCLConvert_Data content section."""
        base_header = "Lane,Sample_ID,Index"
        if self.index_2_cycles:
            base_header = base_header + ",Index2"
        if self.override_cycles:
            base_header = base_header + ",OverrideCycles"
        if self.trim_adapters:
            base_header = base_header + ",AdapterRead1,AdapterRead2"
        if self.barcode_mismatches:
            base_header = base_header + ",BarcodeMismatchesIndex1,BarcodeMismatchesIndex2"
        return base_header + "\n"


class LaneSample:
    run_settings: NovaSeqXRun
    lane: int
    sample_id: str
    index_1: str
    index_2: Optional[str] = None
    adapter_read_1: Optional[str] = None
    adapter_read_2: Optional[str] = None
    barcode_mismatch_index_1: Optional[int]
    barcode_mismatch_index_2: Optional[int]

    def __init__(
        self,
        run_settings: NovaSeqXRun,
        lane: int,
        sample_id: str,
        index_1: str,
        index_2: Optional[str],
        barcode_mismatch_index_1: Optional[int],
        barcode_mismatch_index_2: Optional[int],
    ):
        self.run_settings: NovaSeqXRun = run_settings
        self.lane: int = lane
        self.sample_id: str = sample_id
        self.index_1: str = index_1
        if index_2:
            self.index_2: str = index_2
        # if barcode_mismatch_index_1:
        self.barcode_mismatch_index_1 = barcode_mismatch_index_1
        # if barcode_mismatch_index_2:
        self.barcode_mismatch_index_2 = barcode_mismatch_index_2

    @staticmethod
    def _get_index_override(
        index_length: int,
        index_cycles: int,
        is_backwards: bool = False,
    ):
        """Return override cycles settings of an index."""
        diff: int = index_cycles - index_length
        if diff > 0 and is_backwards:
            return f"N{diff}I{index_length}"
        elif diff > 0 and not is_backwards:
            return f"I{index_length}N{diff}"
        return f"I{index_length}"

    def get_override_cycles(self) -> str:
        """Return override cycles setting for a sample in a lane."""
        read_1_setting: str = f"Y{self.run_settings.read_1_cycles}"
        read_2_setting: str = f"Y{self.run_settings.read_2_cycles}"
        index_1_setting: str = self._get_index_override(
            index_length=len(self.index_1),
            index_cycles=self.run_settings.index_1_cycles,
            is_backwards=False,
        )
        index_2_setting: str = self._get_index_override(
            index_length=len(self.index_2),
            index_cycles=self.run_settings.index_2_cycles,
            is_backwards=True,
        )
        return f"{read_1_setting};{index_1_setting};{index_2_setting};{read_2_setting}"

    def get_bclconversion_data_row(self) -> str:
        """Return the BCLConvert_Data row of a sample in a lane."""
        line: str = f"{self.lane},{self.sample_id},{self.index_1},{self.index_2}"
        if self.run_settings.override_cycles:
            line = line + f",{self.get_override_cycles()}"
        if self.adapter_read_1 or self.adapter_read_2:
            line = line + f",{self.adapter_read_1},{self.adapter_read_2}"
        if self.run_settings.barcode_mismatches:
            line = line + f",{self.barcode_mismatch_index_1},{self.barcode_mismatch_index_2}"
        return line + "\n"
