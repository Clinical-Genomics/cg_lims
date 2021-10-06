from typing import Optional

from genologics.lims import Lims
from pydantic.main import BaseModel
from pydantic import Field
from cg_lims.objects import BaseAnalyte


class AggregateQCDNACovArtifactUDF(BaseModel):
    """Aggregate QC (DNA) (Cov) v1"""

    sample_concentration: Optional[float] = Field(None, alias="Concentration")
    sample_size: Optional[float] = Field(None, alias="Peak Size")


class AggregateQCDNACovUDF(AggregateQCDNACovArtifactUDF):
    class Config:
        allow_population_by_field_name = True


def get_aggregate_qc_dna_cov_udfs(lims: Lims, sample_id: str) -> AggregateQCDNACovUDF:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        artifact_udf_model=AggregateQCDNACovArtifactUDF,
    )

    return AggregateQCDNACovUDF(**analyte.merge_analyte_fields())
