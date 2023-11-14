from cg_lims.enums import IntEnum, FloatEnum, StrEnum


class FlowCellTypes(StrEnum):
    """Flow cell types available from Illumina"""

    FLOW_CELL_10B: str = "10B"
    FLOW_CELL_25B: str = "25B"
    FLOW_CELL_15B: str = "1.5B"


class FlowCellSize(IntEnum):
    """The total number of lanes for a flow cell type."""

    FLOW_CELL_10B: int = 8
    FLOW_CELL_25B: int = 8
    FLOW_CELL_15B: int = 2


class FlowCellLaneVolumes10B(FloatEnum):
    """The recommended volume of reagents per 10B flow cell lane. All values are in ul."""

    POOL_VOLUME: float = 34
    PHIX_VOLUME: float = 1
    NAOH_VOLUME: float = 8.5
    BUFFER_VOLUME: float = 127.5


class FlowCellLaneVolumes15B(FloatEnum):
    """The recommended volume of reagents per 1.5B flow cell lane. All values are in ul."""

    POOL_VOLUME: float = 34
    PHIX_VOLUME: float = 1
    NAOH_VOLUME: float = 8.5
    BUFFER_VOLUME: float = 127.5


class FlowCellLaneVolumes25B(FloatEnum):
    """The recommended volume of reagents per 25B flow cell lane. All values are in ul."""

    POOL_VOLUME: float = 56
    PHIX_VOLUME: float = 1.6
    NAOH_VOLUME: float = 14
    BUFFER_VOLUME: float = 210
