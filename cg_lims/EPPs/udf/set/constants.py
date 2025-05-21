from cg_lims.enums import IntEnum


class DefaultReadLength(IntEnum):
    """Default read length most usually used by each flow cell type."""

    FLOW_CELL_10B: int = 151
    FLOW_CELL_25B: int = 151
    FLOW_CELL_15B: int = 51


class DefaultIndexLength(IntEnum):
    """Default index length most usually used by each flow cell type."""

    FLOW_CELL_10B: int = 10
    FLOW_CELL_25B: int = 10
    FLOW_CELL_15B: int = 10
