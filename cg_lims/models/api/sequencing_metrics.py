from datetime import datetime
from pydantic import BaseModel


class SequencingMetrics(BaseModel):
    flow_cell_name: str
    flow_cell_lane_number: int
    sample_internal_id: str
    sample_total_reads_in_lane: int
    sample_base_fraction_passing_q30: float
    sample_base_mean_quality_score: float
    created_at: datetime
