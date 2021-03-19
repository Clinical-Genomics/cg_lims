from pydantic import BaseModel


class PlacementMapHeader(BaseModel):
    container_name: str
    container_type: str
    container_id: str


class PoolSection(BaseModel):
    nr_samples: int
    pool_name: str
    pool_id: str
    pools_information: str


class SampleTableSection(BaseModel):
    project_name: str
    sample_name: str
    sample_id: str
    orig_cont: str
    orig_well: str
    source_cont: str
    source_well: str
    dest_well: str


class WellInfo(BaseModel):
    project_name: str
    sample_name: str
    sample_id: str
    container_type: str
    container: str
    well_type: str
    well: str
    exta_udf_info: str
