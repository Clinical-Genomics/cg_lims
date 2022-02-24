from typing import Optional

from genologics.entities import Artifact, Process
from pydantic import Field, validator

from cg_lims.models.api.master_steps.base_step import (
    get_artifact_udf,
    BaseStep,
    get_process_udf,
)
from cg_lims.get.artifacts import get_latest_artifact


class KAPALibraryPreparation(BaseStep):
    "KAPA Library Preparation"
    artifact: Optional[Artifact]
    process: Optional[Process]

    label: Optional[str] = Field(None, alias="label (= index)")
    method_document: Optional[str] = Field(None, alias="Method document")
    document_version: Optional[int] = Field(None, alias="Document version")
    prep_kit: Optional[str] = Field(None, alias="KAPA HyperPlus/Prep Kit")
    well: Optional[str] = Field(None, alias="Well")
    container_name: Optional[str] = Field(None, alias="Container Name")
    size_bp: Optional[int]
    concentration: Optional[str]

    @validator("artifact", always=True)
    def get_artifact(cls, v, values):
        try:
            return get_latest_artifact(
                lims=values.get("lims"),
                sample_id=values.get("sample_id"),
                process_types=["KAPA Library Preparation TWIST v1"],
            )
        except:
            return None

    @validator("process", always=True)
    def get_process(cls, v, values):
        if values.get("artifact"):
            return values.get("artifact").parent_process
        return None

    @validator("method_document", always=True)
    def get_method_document(cls, v, values):
        return get_process_udf(values.get("process"), "Method document")

    @validator("document_version", always=True)
    def get_document_version(cls, v, values):
        return get_process_udf(values.get("process"), "Document version")

    @validator("prep_kit", always=True)
    def get_prep_kit(cls, v, values):
        return get_process_udf(values.get("process"), "KAPA HyperPlus/Prep Kit")

    @validator("container_name", always=True)
    def get_container_name(cls, v, values):
        artifact = values.get("artifact")
        if artifact:
            return artifact.container.name
        return None

    @validator("well", always=True)
    def get_well(cls, v, values):
        artifact = values.get("artifact")
        if artifact:
            return artifact.location[1]
        return None

    @validator("label", always=True)
    def get_kapa_label(cls, v, values):
        artifact = values.get("artifact")
        if artifact:
            return artifact.reagent_labels
        return None

    @validator("size_bp", always=True)
    def get_kapa_size_bp(cls, v, values):
        return get_artifact_udf(values.get("artifact"), "Size (bp)")

    @validator("concentration", always=True)
    def get_kapa_concentration(cls, v, values):
        return get_artifact_udf(values.get("artifact"), "Concentration")
