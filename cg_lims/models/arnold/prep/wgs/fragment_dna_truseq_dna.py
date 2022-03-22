from typing import Optional

from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.objects import BaseAnalyte
from cg_lims.models.arnold.prep.base_step import BaseStep


class ProcessUDFS(BaseModel):
    lot_nr_covaris_tube: Optional[str] = Field(None, alias="Lot no: Covaris tube")
    fragmentation_method: Optional[str] = Field(None, alias="Method Document 1")
    covaris_protocol: Optional[str] = Field(None, alias="Protocol")
    lot_nr_resuspension_buffer_fragmentation: Optional[str] = Field(
        None, alias="Lot no: Resuspension Buffer"
    )


class ArnoldStep(BaseStep):
    process_udfs: ProcessUDFS

    class Config:
        allow_population_by_field_name = True


def get_fragemnt_dna_truseq(lims: Lims, sample_id: str, prep_id: str) -> ArnoldStep:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_type="Fragment DNA (TruSeq DNA)",
    )

    return ArnoldStep(
        **analyte.base_fields(),
        process_udfs=ProcessUDFS(**analyte.process_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="fragment_dna",
        workflow="WGS",
    )
