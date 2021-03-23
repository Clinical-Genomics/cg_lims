from pydantic import BaseModel


class PlacementMapHeader(BaseModel):
    process_type: str
    date: str


class PlateInfo(BaseModel):
    container_name: str
    container_type: str
    container_id: str


class WellInfo(BaseModel):
    project_name: str
    sample_name: str
    sample_id: str
    container_source: str
    container_name: str
    well_source: str
    well: str
    exta_udf_info: str
    dest_well: str
    sample_type: str
