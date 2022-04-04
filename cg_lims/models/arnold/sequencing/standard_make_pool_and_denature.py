from typing import Optional

from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.models.arnold.base_step import BaseStep
from cg_lims.objects import BaseAnalyte


class ProcessUDFs(BaseModel):
    """STANDARD Make Pool and Denature (Nova Seq)"""

    volume_of_pool: Optional[str] = Field(None, alias="Volume of Pool to Denature (ul")
    tris_lot_nr: Optional[str] = Field(None, alias="Tris-HCl lot nr")
    naoh_lot_nr: Optional[str] = Field(None, alias="NaOH lot nr")
    phix_lot_nr: Optional[str] = Field(None, alias="PhiX lot nr")
    tris_volume: Optional[str] = Field(None, alias="Tris-HCl Volume (ul)")
    naoh_volume: Optional[str] = Field(None, alias="NaOH Volume (ul)")
    phix_volume: Optional[str] = Field(None, alias="PhiX Volume (ul)")


class ArnoldStep(BaseStep):
    process_udfs: ProcessUDFs

    class Config:
        allow_population_by_field_name = True


def get_standard_make_pool_and_denature(
    lims: Lims, sample_id: str, prep_id: str
) -> Optional[ArnoldStep]:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_type="STANDARD Make Pool and Denature (Nova Seq)",
        optional_step=True,
    )
    if not analyte.process:
        return None

    return ArnoldStep(
        **analyte.base_fields(),
        process_udfs=ProcessUDFs(**analyte.process_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="standard_make_pool_and_denature",
        workflow="NovaSeq"
    )
