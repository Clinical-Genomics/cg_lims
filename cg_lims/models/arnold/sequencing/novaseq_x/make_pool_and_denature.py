from typing import Optional

from cg_lims.models.arnold.base_step import BaseStep
from cg_lims.objects import BaseAnalyte
from genologics.lims import Lims
from pydantic.v1 import Field
from pydantic.v1.main import BaseModel


class ProcessUDFs(BaseModel):
    """Make Pool and Denature (NovaSeq X)"""

    flowcell_type: Optional[str] = Field(None, alias="Flow Cell Type")
    volume_of_pool: Optional[str] = Field(None, alias="Volume of Pool to Denature (ul)")
    lanes_to_load: Optional[str] = Field(None, alias="Lanes to Load")
    buffer_lot_nr: Optional[str] = Field(None, alias="Pre-load Buffer lot nr")
    naoh_lot_nr: Optional[str] = Field(None, alias="NaOH lot nr")
    phix_lot_nr: Optional[str] = Field(None, alias="PhiX lot nr")
    buffer_volume: Optional[str] = Field(None, alias="Pre-load Buffer Volume (ul)")
    naoh_volume: Optional[str] = Field(None, alias="NaOH Volume (ul)")
    phix_volume: Optional[str] = Field(None, alias="PhiX Volume (ul)")


class ArnoldStep(BaseStep):
    process_udfs: ProcessUDFs

    class Config:
        allow_population_by_field_name = True


def get_make_pool_and_denature(lims: Lims, sample_id: str, prep_id: str) -> ArnoldStep:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_type="Make Pool and Denature (NovaSeq X)",
    )

    return ArnoldStep(
        **analyte.base_fields(),
        process_udfs=ProcessUDFs(**analyte.process_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="make_pool_and_denature_x",
        workflow="NovaSeq X"
    )
