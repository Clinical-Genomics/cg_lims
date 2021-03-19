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
    source_well: str
    source_container: str
    pool_name: str
    extra_sample_values: str
