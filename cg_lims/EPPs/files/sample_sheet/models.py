from genologics.lims import Process
from typing import Optional
import logging

LOG = logging.getLogger(__name__)


class SampleSheetHeader:
    FILE_SECTION: str = "[Header]"
    READS_SECTION: str = "[Reads]"
    SETTINGS_SECTION: str = "[Sequencing_Settings]"
    BCL_SETTINGS_SECTION: str = "[BCLConvert_Settings]"
    BCL_DATA_SECTION: str = "[BCLConvert_Data]"


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
    bclconvert_app_version: str
    fastq_compression_format: str
    trim_adapters: Optional[bool] = False

    def __init__(self, process):
        self.process = process
        self.run_name = process.udf.get("Experiment Name")
        self.instrument_type = "NovaSeqxPlus"
        self.instrument_platform = "NovaSeqXSeries"
        self.index_orientation = "Forward"
        self.read_1_cycles = process.udf.get("Read 1 Cycles")
        self.read_2_cycles = process.udf.get("Read 2 Cycles")
        self.index_1_cycles = process.udf.get("Index Read 1")
        self.index_2_cycles = process.udf.get("Index Read 2")
        self.bclconvert_software_version = "4.1.5"
        self.bclconvert_app_version = "4.1.5"
        self.fastq_compression_format = "gzip"

    def create_file_header_section(self) -> str:
        return (
            f"{SampleSheetHeader.FILE_SECTION},\n"
            f"FileFormatVersion,{self.file_format}\n"
            f"RunName,{self.run_name}\n"
            f"InstrumentType,{self.instrument_type}\n"
            f"InstrumentPlatform,{self.instrument_platform}\n"
            f"IndexOrientation,{self.index_orientation}\n\n"
        )

    def create_reads_section(self) -> str:
        return (
            f"{SampleSheetHeader.READS_SECTION}\n"
            f"Read1Cycles,{self.read_1_cycles}\n"
            f"Read2Cycles,{self.read_2_cycles}\n"
            f"Index1Cycles,{self.index_1_cycles}\n"
            f"Index2Cycles,{self.index_2_cycles}\n\n"
        )

    def get_bcl_data_header(self) -> str:
        base_header = "Lane,Sample_ID,Index"
        if self.index_2_cycles:
            base_header = base_header + ",Index2"
        if self.override_cycles:
            base_header = base_header + ",OverrideCycles"
        if self.trim_adapters:
            base_header = base_header + ",AdapterRead1,AdapterRead2"
        return base_header + "\n"


class LaneSample:
    run_settings: NovaSeqXRun
    lane: int
    sample_id: str
    index_1: str
    index_2: Optional[str] = None
    adapter_read_1: Optional[str] = None
    adapter_read_2: Optional[str] = None
    barcode_mismatch_index_1: Optional[int] = None
    barcode_mismatch_index_2: Optional[int] = None

    def __init__(
        self,
        run_settings: NovaSeqXRun,
        lane: int,
        sample_id: str,
        index1: str,
        index2: Optional[str],
    ):
        self.run_settings = run_settings
        self.lane = lane
        self.sample_id = sample_id
        self.index_1 = index1
        if index2:
            self.index_2 = index2

    @staticmethod
    def _get_index_override(
        index_length: int,
        index_cycles: int,
        backwards: bool = False,
    ):
        diff = index_cycles - index_length
        if diff > 0 and backwards:
            return f"N{diff}I{index_length}"
        elif diff > 0 and not backwards:
            return f"I{index_length}N{diff}"
        else:
            return f"I{index_length}"

    def get_override_cycles(self) -> str:
        read_1_setting = f"Y{self.run_settings.read_1_cycles}"
        read_2_setting = f"Y{self.run_settings.read_2_cycles}"
        index_1_setting = self._get_index_override(
            index_length=len(self.index_1),
            index_cycles=self.run_settings.index_1_cycles,
            backwards=False,
        )
        index_2_setting = self._get_index_override(
            index_length=len(self.index_2),
            index_cycles=self.run_settings.index_2_cycles,
            backwards=True,
        )
        return f"{read_1_setting};{index_1_setting};{index_2_setting};{read_2_setting}"

    def get_bclconversion_data(self) -> str:
        line = f"{self.lane},{self.sample_id},{self.index_1},{self.index_2}"
        if self.run_settings.override_cycles:
            line = line + f",{self.get_override_cycles()}"
        if self.adapter_read_1 or self.adapter_read_2:
            line = line + f",{self.adapter_read_1},{self.adapter_read_2}"
        return line + "\n"
