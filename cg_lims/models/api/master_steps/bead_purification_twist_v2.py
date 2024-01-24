from typing import Optional

from cg_lims.get.artifacts import get_latest_analyte
from cg_lims.models.api.master_steps.base_step import BaseStep, get_artifact_udf
from genologics.entities import Artifact
from pydantic.v1 import Field, validator


class BeadPurificationTWIST(BaseStep):
    "Bead Purification TWIST v2"
    artifact: Optional[Artifact]
    size_bp: Optional[str] = Field(None, alias="Size (bp)")
    concentration: Optional[str] = Field(None, alias="Concentration")

    @validator("artifact", always=True)
    def get_artifact(cls, v, values):
        try:
            return get_latest_analyte(
                lims=values.get("lims"),
                sample_id=values.get("sample_id"),
                process_types=["Bead Purification TWIST v2"],
            )
        except:
            try:
                artifact = get_latest_analyte(
                    lims=values.get("lims"),
                    sample_id=values.get("sample_id"),
                    process_types=["Target enrichment TWIST v1"],
                )
            except:
                artifact = None
        return artifact

    @validator("size_bp", always=True)
    def get_amount_of_sample(cls, v, values):
        return get_artifact_udf(values.get("artifact"), "Size (bp)")

    @validator("concentration", always=True)
    def get_concentration(cls, v, values):
        return get_artifact_udf(values.get("artifact"), "Concentration")
