from typing import Optional

from genologics.entities import Artifact, Process
from pydantic import Field, validator

from cg_lims.models.api.master_steps.base_step import (
    get_artifact_udf,
    BaseStep,
    get_process_udf,
)
from cg_lims.get.artifacts import get_latest_analyte


class AliquotsamplesforenzymaticfragmentationTWIST(BaseStep):
    "Aliquot samples for enzymatic fragmentation TWIST"
    artifact: Optional[Artifact]
    process: Optional[Process]
    performance_NA24143: Optional[str] = Field(None, alias="Batch no Prep Performance NA24143")
    GMCKsolid_HD827: Optional[str] = Field(None, alias="Batch no GMCKsolid-HD827")
    GMSlymphoid_HD829: Optional[str] = Field(None, alias="Batch no GMSlymphoid-HD829")
    GMSmyeloid_HD829: Optional[str] = Field(None, alias="Batch no GMSmyeloid-HD829")
    amount_needed: Optional[str] = Field(None, alias="Amount needed (ng)")

    @validator("artifact", always=True, pre=True)
    def get_artifact(cls, v, values):
        try:
            return get_latest_analyte(
                lims=values.get("lims"),
                sample_id=values.get("sample_id"),
                process_types=["Aliquot samples for enzymatic fragmentation TWIST v2"],
            )
        except:
            return None

    @validator("process", always=True)
    def get_process(cls, v, values):
        if values.get("artifact"):
            return values.get("artifact").parent_process
        return None

    @validator("performance_NA24143", always=True)
    def get_performance_NA24143(cls, v, values):
        return get_process_udf(values.get("process"), "Batch no Prep Performance NA24143")

    @validator("GMCKsolid_HD827", always=True)
    def get_GMCKsolid_HD827(cls, v, values):
        return get_process_udf(values.get("process"), "Batch no GMCKsolid-HD827")

    @validator("GMSlymphoid_HD829", always=True)
    def get_GMSlymphoid_HD829(cls, v, values):
        return get_process_udf(values.get("process"), "Batch no GMSlymphoid-HD829")

    @validator("GMSmyeloid_HD829", always=True)
    def get_GMSmyeloid_HD829(cls, v, values):
        return get_process_udf(values.get("process"), "Batch no GMSmyeloid-HD829")

    @validator("amount_needed", always=True)
    def get_amount_needed(cls, v, values):
        return get_artifact_udf(values.get("artifact"), "Amount needed (ng)")
