from typing import Optional

from cg_lims.get.artifacts import get_latest_analyte
from cg_lims.models.api.master_steps.base_step import BaseStep, get_artifact_udf, get_process_udf
from genologics.entities import Artifact, Process
from pydantic.v1 import Field, validator


class HybridizeLibraryTWIST(BaseStep):
    "Hybridize Library TWIST v2"
    artifact: Optional[Artifact]
    process: Optional[Process]
    bait_set: Optional[str] = Field(None, alias="Bait Set")
    capture_kit: Optional[str] = Field(None, alias="Capture kit lot nr.")
    container_name: Optional[str] = Field(None, alias="Container Name")
    enrichment_kit: Optional[str] = Field(None, alias="Twist enrichment kit")
    blockers: Optional[str] = Field(None, alias="Blockers")
    hybridization_kit: Optional[str] = Field(None, alias="TWIST Hybridization kit")
    thermal_cycler: Optional[str] = Field(None, alias="Thermal cycler")
    method_document: Optional[str] = Field(None, alias="Method document")
    document_version: Optional[str] = Field(None, alias="Document version")

    @validator("artifact", always=True)
    def get_artifact(cls, v, values):
        try:
            return get_latest_analyte(
                lims=values.get("lims"),
                sample_id=values.get("sample_id"),
                process_types=["Hybridize Library TWIST v2"],
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

    @validator("process", always=True)
    def get_process(cls, v, values):
        if values.get("artifact"):
            return values.get("artifact").parent_process
        return None

    @validator("bait_set", always=True)
    def get_bait_set(cls, v, values):
        return get_artifact_udf(values.get("artifact"), "Bait Set")

    @validator("capture_kit", always=True)
    def get_capture_kit(cls, v, values):
        return get_artifact_udf(values.get("artifact"), "Capture kit lot nr.")

    @validator("container_name", always=True)
    def get_container_name(cls, v, values):
        artifact = values.get("artifact")
        if artifact:
            return artifact.container.name
        return None

    @validator("enrichment_kit", always=True)
    def get_enrichment_kit(cls, v, values):
        return get_process_udf(values.get("process"), "Twist enrichment kit")

    @validator("blockers", always=True)
    def get_blockers(cls, v, values):
        return get_process_udf(values.get("process"), "Blockers")

    @validator("hybridization_kit", always=True)
    def get_hybridization_kit(cls, v, values):
        return get_process_udf(values.get("process"), "TWIST Hybridization kit")

    @validator("thermal_cycler", always=True)
    def get_thermal_cycler(cls, v, values):
        thermal_cycler = get_process_udf(values.get("process"), "Thermal cycler")
        if not thermal_cycler:
            thermal_cycler = get_process_udf(values.get("process"), "Thermal cycler (hyb)")
        return thermal_cycler

    @validator("method_document", always=True)
    def get_method_document(cls, v, values):
        return get_process_udf(values.get("process"), "Method document")

    @validator("document_version", always=True)
    def get_document_version(cls, v, values):
        return get_process_udf(values.get("process"), "Document version")
