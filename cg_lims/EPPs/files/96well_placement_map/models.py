from pydantic import BaseModel


class PlacementMapHeader(BaseModel):
    container_name: str
    container_type: str
    container_id: str


class WellInfo(BaseModel):
    project_name: str
    sample_name: str
    sample_id: str
    container_type: str
    container: str
    well_type: str
    well: str
    exta_udf_info: str
    dest_well: str
