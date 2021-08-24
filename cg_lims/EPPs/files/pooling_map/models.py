from typing import Optional

from pydantic import BaseModel


class PlacementMapHeader(BaseModel):
    process_type: str
    date: str


class PoolSection(BaseModel):
    nr_samples: int
    pool_name: str
    pool_id: str
    pools_information: str


class SampleTableSection(BaseModel):
    sample_id: str
    sample_warning_color: Optional[str]
    source_well: str
    source_container: str
    source_container_color: str
    pool_name: str
    extra_sample_values: str
