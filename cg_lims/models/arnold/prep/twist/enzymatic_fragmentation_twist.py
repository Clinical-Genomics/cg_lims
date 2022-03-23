from typing import Optional

from genologics.lims import Lims
from pydantic import Field, BaseModel

from cg_lims.objects import BaseAnalyte
from cg_lims.models.arnold.prep.base_step import BaseStep


class ProcessUdfs(BaseModel):
    fragmentation_method: Optional[str] = Field(None, alias="Method document")
    fragmentation_time: Optional[float] = Field(None, alias="Fragmentation time (min)")
    fragmentation_kit: Optional[str] = Field(None, alias="KAPA HyperPlus Kit")
    fragmentation_instrument_hybridization: Optional[str] = Field(None, alias="Thermal cycler name")
    fragmentation_hamilton: Optional[str] = Field(None, alias="Hamilton")


class ArnoldStep(BaseStep):
    process_udfs: ProcessUdfs

    class Config:
        allow_population_by_field_name = True


def get_enzymatic_fragmentation(lims: Lims, sample_id: str, prep_id: str) -> Optional[ArnoldStep]:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_type="Enzymatic fragmentation TWIST v2",
        optional_step=True,
    )
    if not analyte.artifact:
        return None

    return ArnoldStep(
        **analyte.base_fields(),
        process_udfs=ProcessUdfs(**analyte.process_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="enzymatic_fragmentation",
        workflow="TWIST",
    )
