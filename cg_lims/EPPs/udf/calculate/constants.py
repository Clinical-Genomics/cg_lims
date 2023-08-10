from cg_lims.enums import IntEnum, FloatEnum, StrEnum


class FlowCellTypes(StrEnum):
    """Flow cell types available from Illumina"""

    FLOW_CELL_10B: str = "10B"


class FlowCellSize(IntEnum):
    """The total number of lanes for a flow cell type."""

    FLOW_CELL_10B: int = 8


class FlowCellLaneVolumes10B(FloatEnum):
    """The recommended volume of reagents per flow cell lane. All values are in ul."""

    POOL_VOLUME: float = 34
    PHIX_VOLUME: float = 1
    NAOH_VOLUME: float = 8.5
    BUFFER_VOLUME: float = 127.5
