from pydantic import BaseModel


class SampleLaneSequencingMetrics(BaseModel):
    flow_cell_name: str
    flow_cell_lane_number: int
    sample_internal_id: str
    sample_total_reads_in_lane: int
    sample_base_percentage_passing_q30: float


class PacbioSampleSequencingMetrics(BaseModel):
    smrt_cell_id: str
    sample_id: str
    hifi_yield: int
    hifi_reads: int
    hifi_median_read_quality: str
    hifi_mean_read_length: float


class PacbioSequencingRun(BaseModel):
    barcoded_hifi_mean_read_length: int
    barcoded_hifi_reads: int
    barcoded_hifi_reads_percentage: float
    completed_at: str
    hifi_mean_read_length: int
    hifi_median_read_quality: str
    hifi_reads: int
    hifi_yield: int
    internal_id: str
    movie_name: str
    p0_percent: float
    p1_percent: float
    p2_percent: float
    percent_reads_passing_q30: float
    plate: int
    run_name: str
    started_at: str
    well: str
