from typing import Optional

from genologics.entities import Artifact
from pydantic import BaseModel, Field, validator


class CovidPrepFileRow(BaseModel):
    lims_id: str = Field(alias="LIMS ID")
    sample_well: str = Field(alias="Sample Well")
    destination_well: str = Field(alias="Destination Well")
    index_well: str = Field(alias="Index Well")

    class Config:
        allow_population_by_field_name = True
        # arbitrary_types_allowed = True
        # validate_assignment = True


class BarcodeFileRow(BaseModel):
    source_artifact: Artifact
    destination_artifact: Artifact
    pool: bool
    buffer: bool
    source_labware: Optional[str] = Field(alias="Source Labware")
    barcode_source_container: Optional[str] = Field(alias="Barcode Source Container")
    source_well: Optional[str] = Field(alias="Source Well")
    sample_volume: str = Field(alias="Sample Volume")
    destination_labware: Optional[str] = Field(alias="Destination Labware")
    barcode_destination_container: Optional[str] = Field(alias="Barcode Destination Container")
    destination_well: Optional[str] = Field(alias="Destination Well")
    buffer_volume: str = Field(alias="Buffer Volume")

    @validator("barcode_source_container", always=True, pre=True)
    def set_barcode_source_container(cls, v, values: dict) -> Optional[str]:
        return values["source_artifact"].udf.get("Output Container Barcode")

    @validator("barcode_destination_container", always=True, pre=True)
    def set_barcode_destination_container(cls, v, values: dict) -> Optional[str]:
        return values["destination_artifact"].udf.get("Output Container Barcode")

    @validator("source_labware", always=True, pre=True)
    def set_source_labware(cls, v, values: dict) -> Optional[str]:
        return values["source_artifact"].location[0].type.name

    @validator("destination_labware", always=True, pre=True)
    def set_sdestination_labware(cls, v, values: dict) -> Optional[str]:
        return values["destination_artifact"].location[0].type.name

    @validator("sample_volume", always=True, pre=True)
    def set_sample_volume(cls, v, values: dict) -> str:
        if values["pool"]:
            return values["source_artifact"].udf.get(v)
        else:
            return values["destination_artifact"].udf.get(v)

    @validator("buffer_volume", always=True, pre=True)
    def set_buffer_volume(cls, v, values: dict) -> str:
        if values["buffer"]:
            return values["destination_artifact"].udf.get(v)
        else:
            return 0

    @validator("source_well", always=True, pre=True)
    def set_source_well(cls, v, values: dict) -> str:
        if values["source_labware"] == "Tube":
            return values["barcode_source_container"]
        else:
            return values["source_artifact"].location[1].replace(":", "")

    @validator("destination_well", always=True, pre=True)
    def set_destination_well(cls, v, values: dict) -> str:
        if values["destination_labware"] == "Tube":
            return values["barcode_destination_container"]
        else:
            return values["destination_artifact"].location[1].replace(":", "")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        validate_assignment = True
