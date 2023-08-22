from typing import Optional

from genologics.lims import Lims
from pydantic.v1.main import BaseModel
from pydantic.v1 import Field

from cg_lims.models.arnold.base_step import BaseStep
from cg_lims.objects import BaseAnalyte


class ProcessUDFs(BaseModel):
    """Prepare for Sequencing (NovaSeq X)"""

    run_mode: Optional[str] = Field(None, alias="Run Mode")
    basespace_run_name: Optional[str] = Field(None, alias="BaseSpace Run Name")
    library_tube_strip_id: Optional[str] = Field(None, alias="Library Tube Strip ID")
    index_read_1: Optional[str] = Field(None, alias="Index Read 1")
    index_read_2: Optional[str] = Field(None, alias="Index Read 2")
    read_1_cycles: Optional[str] = Field(None, alias="Read 1 Cycles")
    read_2_cycles: Optional[str] = Field(None, alias="Read 2 Cycles")
    bclconvert_software_version: Optional[str] = Field(None, alias="BCLConvert Software Version")


class ArnoldStep(BaseStep):
    process_udfs: ProcessUDFs

    class Config:
        allow_population_by_field_name = True


def get_prepare_for_sequencing(lims: Lims, sample_id: str, prep_id: str) -> Optional[ArnoldStep]:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_type="Prepare for Sequencing (NovaSeq X)",
        optional_step=True,
    )
    if not analyte.process:
        return None
    return ArnoldStep(
        **analyte.base_fields(),
        process_udfs=ProcessUDFs(**analyte.process_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="prepare_for_sequencing_x",
        workflow="NovaSeq X"
    )
