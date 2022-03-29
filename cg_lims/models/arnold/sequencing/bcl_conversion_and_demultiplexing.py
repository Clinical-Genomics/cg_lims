from typing import Optional

from genologics.lims import Lims, Process
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.models.arnold.base_step import BaseStep
from cg_lims.objects import BclConversionAnalyte


class ProcessUDFs(BaseModel):
    """Bcl Conversion & Demultiplexing (Nova Seq)"""

    method_document: Optional[str] = Field(None, alias="Method Document")  # and atlas version pudf?
    pct_Q30_bases_threshold: Optional[str] = Field(
        None, alias="Threshold for % bases >= Q30"
    )  # keep or not?


class ArtifactUDFs(BaseModel):
    # Needs rework after new class BclConversionStep is completed
    pct_bases_over_q30: Optional[float]
    number_of_reads: Optional[float]


class ArnoldStep(BaseStep):
    process_udfs: ProcessUDFs
    artifact_udfs: ArtifactUDFs

    class Config:
        allow_population_by_field_name = True


def get_bcl_conversion_and_demultiplexing(
    lims: Lims, sample_id: str, prep_id: str, process_id: str
) -> ArnoldStep:
    process = Process(lims, id=process_id)
    bcl_analyte = BclConversionAnalyte(
        lims=lims,
        sample_id=sample_id,
        q30_udf="% Bases >=Q30",
        sum_reads_udf="# Reads",
        process=process,
    )

    return ArnoldStep(
        process_udfs=ProcessUDFs(**dict(process.udf.items())),
        artifact_udfs=ArtifactUDFs(
            pct_bases_over_q30=bcl_analyte.get_average_q30(),
            number_of_reads=bcl_analyte.get_sum_reads(),
        ),
        lims_step_name=process.type.name,
        date_run=process.date_run,
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="bcl_conversion_and_demultiplexing",
        workflow="NovaSeq",
    )
