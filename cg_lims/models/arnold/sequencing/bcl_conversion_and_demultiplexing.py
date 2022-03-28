from typing import Optional

from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.models.arnold.base_step import BaseStep
from cg_lims.objects import BaseAnalyte


class ProcessUDFs(BaseModel):
    """Bcl Conversion & Demultiplexing (Nova Seq)"""

    method_document: Optional[str] = Field(None, alias="Method Document") # and atlas version pudf?
    pct_Q30_bases_threshold: Optional[str] = Field(None, alias="Threshold for % bases >= Q30") # keep or not?


class ArtifactUDFs(BaseModel):
    # Needs rework after new class BclConversionStep is completed
    pct_perfect_index_reads: Optional[float] = Field(None, alias="% Perfect Index Read")
    pct_bases_over_q30: Optional[float] = Field(None, alias="% Bases >=Q30")
    number_of_reads: Optional[float] = Field(None, alias="# Reads")


class ArnoldStep(BaseStep):
    process_udfs: ProcessUDFs
    artifact_udfs: ArtifactUDFs

    class Config:
        allow_population_by_field_name = True


def get_bcl_conversion_and_demultiplexing(lims: Lims, sample_id: str, prep_id: str) -> ArnoldStep:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_type="Bcl Conversion & Demultiplexing (Nova Seq)",
    )

    return ArnoldStep(
        **analyte.base_fields(),
        process_udfs=ProcessUDFs(**analyte.process_udfs()),
        artifact_udfs=ArtifactUDFs(**analyte.artifact_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="bcl_conversion_and_demultiplexing",
        workflow="NovaSeq"
    )
