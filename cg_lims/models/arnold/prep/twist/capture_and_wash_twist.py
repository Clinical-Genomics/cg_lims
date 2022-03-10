from genologics.lims import Lims
from pydantic import Field, BaseModel

from cg_lims.objects import BaseAnalyte
from cg_lims.models.arnold.prep.base_step import BaseStep


class ProcessUDFs(BaseModel):
    hybridization_time: float = Field(..., alias="Total hybridization time (h)")
    lot_nr_h20_capture_and_wash: str = Field(..., alias="Nuclease free water")
    capture_and_wash_method: str = Field(..., alias="Method document")
    binding_and_purification_beads: str = Field(..., alias="Twist Binding and Purification beads")
    wash_buffers: str = Field(..., alias="Twist Wash Buffers")


class ArnoldStep(BaseStep):
    process_udfs: ProcessUDFs

    class Config:
        allow_population_by_field_name = True


def get_capture_and_wash(lims: Lims, sample_id: str, prep_id: str) -> ArnoldStep:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_type="Capture and Wash TWIST v2",
    )

    return ArnoldStep(
        **analyte.base_fields(),
        process_udfs=ProcessUDFs(**analyte.process_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="capture_and_wash",
        workflow="TWIST",
    )
