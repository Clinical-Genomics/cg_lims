from statistics import mean
from typing import Optional, List

from genologics.lims import Lims, Process, Artifact
from pydantic.main import BaseModel
from pydantic import Field

from cg_lims.get.artifacts import get_artifacts
from cg_lims.models.arnold.base_step import BaseStep


class ProcessUDFs(BaseModel):
    """Bcl Conversion & Demultiplexing (Nova Seq)"""

    methods: Optional[str] = Field(None, alias="Methods")
    atlas_version: Optional[str] = Field(None, alias="Atlas Version")
    pct_Q30_bases_threshold: Optional[str] = Field(None, alias="Threshold for % bases >= Q30")


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
        try:
            sum_reads += int(artifact.udf.get(sum_reads_udf))
        except ValueError:
            return None

    return sum_reads


def get_average_q30(q30_udf: str, artifacts: List[Artifact]) -> Optional[float]:
    q_30 = []
    for artifact in artifacts:
        try:
            q_30.append(float(artifact.udf.get(q30_udf)))
        except ValueError:
            return None
    return mean(q_30)


def get_bcl_conversion_and_demultiplexing(
    lims: Lims, sample_id: str, prep_id: str, process_id: str
) -> ArnoldStep:
    process = Process(lims, id=process_id)
    process.get()
    artifacts = get_artifacts(process=process, reagent_label=True)
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
