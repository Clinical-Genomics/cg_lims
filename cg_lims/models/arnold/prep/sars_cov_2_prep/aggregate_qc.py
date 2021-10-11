from typing import Optional

from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field
from cg_lims.objects import BaseAnalyte
from cg_lims.models.arnold.prep.base_step import BaseStep


class AggregateQCDNACovArtifactUDF(BaseModel):
    """Aggregate QC (DNA) (Cov) v1"""

    sample_concentration: Optional[float] = Field(None, alias="Concentration")
    sample_size: Optional[float] = Field(None, alias="Size (bp)")


class AggregateQCDNACovFields(BaseStep):
    artifact_udfs: AggregateQCDNACovArtifactUDF

    class Config:
        allow_population_by_field_name = True


def get_aggregate_qc_dna_cov_udfs(
    lims: Lims, sample_id: str, prep_id: str
) -> AggregateQCDNACovFields:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        optional_step=True,
    )

    return AggregateQCDNACovFields(
        **analyte.base_fields(),
        artifact_udfs=AggregateQCDNACovArtifactUDF(**analyte.artifact_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="aggregate_qc_dna",
        workflow="sars_cov_2"
    )
