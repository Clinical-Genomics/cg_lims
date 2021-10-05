from typing import Optional

from genologics.lims import Lims
from pydantic import Field, BaseModel

from cg_lims.objects import BaseAnalyte


class CaptureandWashProcessUDFs(BaseModel):
    enrichment_kit_capture_and_wash: Optional[str] = Field(None, alias="Twist enrichment kit")
    hybridization_time: str = Field(..., alias="Total hybridization time (h)")
    lot_nr_h20_capture_and_wash: str = Field(..., alias="Nuclease free water")
    capture_and_wash_method: str = Field(..., alias="Method document")
        
    # well position 
    # container name


class CaptureandWashUDFs(CaptureandWashProcessUDFs):
    class Config:
        allow_population_by_field_name = True


def get_capture_and_wash(lims: Lims, sample_id: str) -> CaptureandWashUDFs:
    capture_and_wash = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_udf_model=CaptureandWashProcessUDFs,
        process_type="Capture and Wash TWIST v2",
    )

    return CaptureandWashUDFs(**capture_and_wash.merge_process_and_artifact_udfs())
