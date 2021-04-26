from typing import Optional

from genologics.entities import Process, Artifact
from genologics.lims import Lims
from pydantic import BaseModel, Field, validator

from cg_lims.get.artifacts import get_latest_artifact


def get_artifact_udf(artifact, udf):
    if artifact:
        return artifact.udf.get(udf)
    return None


def get_process_udf(process, udf):
    if process:
        return process.udf.get(udf)
    return None


class BaseStep(BaseModel):
    sample_id: str
    lims: Lims

    class Config:
        arbitrary_types_allowed = True


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
            return get_latest_artifact(
                lims=values.get("lims"),
                sample_id=values.get("sample_id"),
                process_type=["Hybridize Library TWIST v2"],
            )
        except:
            return None

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
        return get_process_udf(values.get("process"), "Thermal cycler")

    @validator("method_document", always=True)
    def get_method_document(cls, v, values):
        return get_process_udf(values.get("process"), "Method document")

    @validator("document_version", always=True)
    def get_document_version(cls, v, values):
        return get_process_udf(values.get("process"), "Document version")


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
            return get_latest_artifact(
                lims=values.get("lims"),
                sample_id=values.get("sample_id"),
                process_type=["Aliquot samples for enzymatic fragmentation TWIST v2"],
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
                process_type=["KAPA Library Preparation TWIST v1"],
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


class PoolsamplesforhybridizationTWIST(BaseStep):
    "pool samples TWIST v2"
    artifact: Optional[Artifact]
    process: Optional[Process]
    amount_of_sample: Optional[str] = Field(None, alias="Total Amount (ng)")

    @validator("artifact", always=True)
    def get_artifact(cls, v, values):
        try:
            return get_latest_artifact(
                lims=values.get("lims"),
                sample_id=values.get("sample_id"),
                process_type=["pool samples TWIST v2"],
            )
        except:
            return None

    @validator("process", always=True)
    def get_process(cls, v, values):
        if values.get("artifact"):
            return values.get("artifact").parent_process
        return None

    @validator("amount_of_sample", always=True)
    def get_amount_of_sample(cls, v, values):
        return get_artifact_udf(values.get("artifact"), "Total Amount (ng)")


class CaptureandWashTWIST(BaseStep):
    "Capture and Wash TWIST v2"
    artifact: Optional[Artifact]
    process: Optional[Process]
    enrichment_kit: Optional[str] = Field(None, alias="Twist enrichment kit")
    hybridization_time: Optional[str] = Field(None, alias="Total hybridization time (h)")

    @validator("artifact", always=True)
    def get_artifact(cls, v, values):
        try:
            return get_latest_artifact(
                lims=values.get("lims"),
                sample_id=values.get("sample_id"),
                process_type=["Capture and Wash TWIST v2"],
            )
        except:
            return None

    @validator("process", always=True)
    def get_process(cls, v, values):
        if values.get("artifact"):
            return values.get("artifact").parent_process
        return None

    @validator("enrichment_kit", always=True)
    def get_enrichment_kit(cls, v, values):
        return get_process_udf(values.get("process"), "Twist enrichment kit")

    @validator("hybridization_time", always=True)
    def get_hybridization_time(cls, v, values):
        return get_process_udf(values.get("process"), "Total hybridization time (h)")


class BeadPurificationTWIST(BaseStep):
    "Bead Purification TWIST v2"
    artifact: Optional[Artifact]
    size_bp: Optional[str] = Field(None, alias="Size (bp)")
    concentration: Optional[str] = Field(None, alias="Concentration")

    @validator("artifact", always=True)
    def get_artifact(cls, v, values):
        try:
            return get_latest_artifact(
                lims=values.get("lims"),
                sample_id=values.get("sample_id"),
                process_type=["Bead Purification TWIST v2"],
            )
        except:
            return None

    @validator("size_bp", always=True)
    def get_amount_of_sample(cls, v, values):
        return get_artifact_udf(values.get("artifact"), "Size (bp)")

    @validator("concentration", always=True)
    def get_concentration(cls, v, values):
        return get_artifact_udf(values.get("artifact"), "Concentration")


class BufferExchange(BaseStep):
    artifact: Optional[Artifact]
    concentration: Optional[str] = Field(None, alias="Concentration")

    @validator("artifact", always=True)
    def get_artifact(cls, v, values):
        try:
            return get_latest_artifact(
                lims=values.get("lims"),
                sample_id=values.get("sample_id"),
                process_type=["Buffer Exchange v2"],
            )
        except:
            return None

    @validator("concentration", always=True)
    def get_size_bp(cls, v, values):
        return get_artifact_udf(values.get("artifact"), "Concentration")


class ReceptionControlTWIST(BaseModel):
    "Reception Control TWIST"


class BufferExchangeTWIST(BaseModel):
    "Buffer Exchange TWIST"


class EnzymaticfragmentationTWIST(BaseModel):
    "Enzymatic fragmentation TWIST"


class LibraryValidationQCTWISTv2(BaseModel):
    "Library Validation QC TWIST v2"


class TapestationReceptionControlTWIST(BaseModel):
    "Tapestation Reception Control TWIST"


class AmplifyCapturedLibrariesTWIST(BaseModel):
    "T"


class QubitQCDNATWIST(BaseModel):
    "Qubit QC (DNA) TWIST"


class QuantitQCDNATWIST(BaseModel):
    "Quantit QC (DNA) TWIST"
    concentration: Optional[float] = Field(None, alias="Concentration")


class AggregateQCDNATWIST(BaseModel):
    "Aggregate QC (DNA) TWIST"
    size_bp: Optional[float] = Field(None, alias="Size (bp)")


class TapestationQCTWIST(BaseModel):
    "Tapestation QC TWIST"
    size_bp: Optional[float] = Field(None, alias="Size (bp)")


class QubitQCLibraryValidationTWIST(BaseModel):
    "Qubit QC (Library Validation) TWIST"
    concentration: Optional[float] = Field(None, alias="Concentration")


class QuantitQCLibraryValidationTWIST(BaseModel):
    "Quantit QC (Library Validation) TWIST"
    concentration: Optional[float] = Field(None, alias="Concentration")


class AggregateQCLibraryValidationTWIST(BaseModel):
    "Aggregate QC (Library Validation) TWIST"
