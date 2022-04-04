from statistics import mean
from typing import Optional, List

from genologics.lims import Lims, Process, Artifact
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.get.artifacts import get_output_artifacts_by_output_generation_type
from cg_lims.models.arnold.base_step import BaseStep


class ProcessUDFs(BaseModel):
    """Bcl Conversion & Demultiplexing (Nova Seq)"""

    method_document: Optional[str] = Field(None, alias="Method Document")  # and atlas version pudf?
    pct_Q30_bases_threshold: Optional[str] = Field(
        None, alias="Threshold for % bases >= Q30"
    )  # keep or not?


class ArtifactUDFs(BaseModel):
    pct_bases_over_q30: Optional[float]
    number_of_reads: Optional[float]


class ArnoldStep(BaseStep):
    process_udfs: ProcessUDFs
    artifact_udfs: ArtifactUDFs

    class Config:
        allow_population_by_field_name = True


def get_sum_reads(sum_reads_udf: str, artifacts: List[Artifact]) -> Optional[int]:
    sum_reads = 0
    for artifact in artifacts:
        if not isinstance(artifact.udf.get(sum_reads_udf), int):
            return None
        sum_reads += artifact.udf.get(sum_reads_udf)

    return sum_reads


def get_average_q30(q30_udf: str, artifacts: List[Artifact]) -> Optional[float]:
    q_30 = []
    for artifact in artifacts:
        if not isinstance(artifact.udf.get(q30_udf), float):
            return None
        q_30.append(artifact.udf.get(q30_udf))

    return mean(q_30)


def get_bcl_conversion_and_demultiplexing(
    lims: Lims, sample_id: str, prep_id: str, process_id: str
) -> ArnoldStep:
    process = Process(lims, id=process_id)

    artifacts = get_output_artifacts_by_output_generation_type(
        process=process, output_generation_type="PerReagentLabel", lims=lims
    )

    return ArnoldStep(
        process_udfs=ProcessUDFs(**dict(process.udf.items())),
        artifact_udfs=ArtifactUDFs(
            pct_bases_over_q30=get_average_q30(artifacts=artifacts, q30_udf="% Bases >=Q30"),
            number_of_reads=get_sum_reads(artifacts=artifacts, sum_reads_udf="# Reads"),
        ),
        lims_step_name=process.type.name,
        date_run=process.date_run,
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="bcl_conversion_and_demultiplexing",
        workflow="NovaSeq",
    )
