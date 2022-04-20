from typing import Optional

from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.models.arnold.base_step import BaseStep
from cg_lims.objects import BaseAnalyte


class ProcessUDFs(BaseModel):
    """Xp Load to FlowCell (Nova Seq)"""

    workflow_type: Optional[str] = Field(None, alias="Workflow Type")
    paired_end: Optional[str] = Field(None, alias="Paired End")
    index_read_1: Optional[str] = Field(None, alias="Index Read 1")
    index_read_2: Optional[str] = Field(None, alias="Index Read 2")
    read_1_cycles: Optional[str] = Field(None, alias="Read 1 Cycles")
    read_2_cgitycles: Optional[str] = Field(None, alias="Read 2 Cycles")


class ArnoldStep(BaseStep):
    process_udfs: ProcessUDFs

    class Config:
        allow_population_by_field_name = True


def get_xp_load_to_flowcell(lims: Lims, sample_id: str, prep_id: str) -> Optional[ArnoldStep]:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_type="Xp Load to FlowCell (Nova Seq)",
        optional_step=True,
    )
    if not analyte.process:
        return None
    return ArnoldStep(
        **analyte.base_fields(),
        process_udfs=ProcessUDFs(**analyte.process_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="xp_load_to_flowcell",
        workflow="NovaSeq"
    )
