import csv
from typing import List

import click
import yaml
from genologics.lims import Lims
from pydantic import BaseModel, Field

from cg_lims.app.schemas.master_steps import (
    HybridizeLibraryTWIST,
    AliquotsamplesforenzymaticfragmentationTWIST,
    KAPALibraryPreparation,
    PoolsamplesforhybridizationTWIST,
    CaptureandWashTWIST,
    BeadPurificationTWIST,
    BufferExchange,
)


HEADERS = [
    "SampleID",
    "HybridizeBaitSet",
    "HybridizeCaptureKit",
    "HybridizeContainerName",
    "HybridizeTwistEnrichmentKit",
    "HybridizeBlockers",
    "HybridizeKit",
    "HybridizeThermalCycler",
    "HybridizeMethodDocument",
    "HybridizeDocumentVersion",
    "AliquotBatchNoPrepPerformanceNA24143",
    "AliquotBatchNoGMCKsolidHD827",
    "AliquotBatchNoGMSlymphoidHD829",
    "AliquotBatchNoGMSmyeloidHD829",
    "AliquotAmountNeeded",
    "KapaLabel",
    "KapaMethodDocument",
    "KapaDocumentVersion",
    "KapaPrepKit",
    "KapaWell",
    "KapaContainerName",
    "PreHybLibrarySize",
    "PreHybConcentration",
    "PoolAmount",
    "CaptureEnrichmentKit",
    "CaptureHybridizationTime",
    "BufferExchangeConcentration",
    "PostHybLibrarySize",
    "PostHybConcentration",
]


class DebugKapaCSV(BaseModel):
    sample_id: str = Field(..., alias="SampleID")
    hyb_bait_set: str = Field(None, alias="HybridizeBaitSet")
    hyb_capture_kit: str = Field(None, alias="HybridizeCaptureKit")
    hyb_container_name: str = Field(None, alias="HybridizeContainerName")
    hyb_enrichment_kit: str = Field(None, alias="HybridizeTwistEnrichmentKit")
    hyb_blockers: str = Field(None, alias="HybridizeBlockers")
    hyb_kit: str = Field(None, alias="HybridizeKit")
    hyb_thermal_cycler: str = Field(None, alias="HybridizeThermalCycler")
    hyb_method_document: str = Field(None, alias="HybridizeMethodDocument")
    hyb_document_version: str = Field(None, alias="HybridizeDocumentVersion")
    aliquot_performance_NA24143: str = Field(None, alias="AliquotBatchNoPrepPerformanceNA24143")
    aliquot_GMCKsolid_HD827: str = Field(None, alias="AliquotBatchNoGMCKsolidHD827")
    aliquot_GMSlymphoid_HD829: str = Field(None, alias="AliquotBatchNoGMSlymphoidHD829")
    aliquot_GMSmyeloid_HD829: str = Field(None, alias="AliquotBatchNoGMSmyeloidHD829")
    aliquot_amount_needed: str = Field(None, alias="AliquotAmountNeeded")
    kapa_label: str = Field(None, alias="KapaLabel")
    kapa_method_document: str = Field(None, alias="KapaMethodDocument")
    kapa_document_version: str = Field(None, alias="KapaDocumentVersion")
    kapa_kit: str = Field(None, alias="KapaPrepKit")
    kapa_well: str = Field(None, alias="KapaWell")
    kapa_container_name: str = Field(None, alias="KapaContainerName")
    kapa_size_bp: str = Field(None, alias="PreHybLibrarySize")
    kapa_concentration: str = Field(None, alias="PreHybConcentration")
    pool_amount_of_sample: str = Field(None, alias="PoolAmount")
    capt_enrichment_kit: str = Field(None, alias="CaptureEnrichmentKit")
    capt_hybridization_time: str = Field(None, alias="CaptureHybridizationTime")
    bead_size_bp: str = Field(None, alias="PostHybLibrarySize")
    bead_concentration: str = Field(None, alias="PostHybConcentration")
    buff_concentration: str = Field(None, alias="BufferExchangeConcentration")

    class Config:
        arbitrary_types_allowed = True

    def set_hybridize(self, hybridize: HybridizeLibraryTWIST):
        self.hyb_bait_set = hybridize.bait_set
        self.hyb_capture_kit = hybridize.capture_kit
        self.hyb_container_name = hybridize.container_name
        self.hyb_enrichment_kit = hybridize.enrichment_kit
        self.hyb_blockers = hybridize.blockers
        self.hyb_kit = hybridize.hybridization_kit
        self.hyb_thermal_cycler = hybridize.thermal_cycler
        self.hyb_method_document = hybridize.method_document
        self.hyb_document_version = hybridize.document_version

    def set_aliquot(self, aliquot):
        self.aliquot_performance_NA24143 = aliquot.performance_NA24143
        self.aliquot_GMCKsolid_HD827 = aliquot.GMCKsolid_HD827
        self.aliquot_GMSlymphoid_HD829 = aliquot.GMSlymphoid_HD829
        self.aliquot_GMSmyeloid_HD829 = aliquot.GMSmyeloid_HD829
        self.aliquot_amount_needed = aliquot.amount_needed

    def set_kapa(self, kapa):
        self.kapa_label = kapa.label
        self.kapa_method_document = kapa.method_document
        self.kapa_document_version = kapa.document_version
        self.kapa_kit = kapa.prep_kit
        self.kapa_well = kapa.well
        self.kapa_container_name = kapa.container_name
        self.kapa_size_bp = kapa.size_bp
        self.kapa_concentration = kapa.concentration

    def set_pool(self, pool):
        self.pool_amount_of_sample = pool.amount_of_sample

    def set_capture(self, capture):
        self.capt_enrichment_kit = capture.enrichment_kit
        self.capt_hybridization_time = capture.hybridization_time

    def set_bead(self, bead):
        self.bead_size_bp = bead.size_bp
        self.bead_concentration = bead.concentration

    def set_buffer(self, buffer):
        self.buff_concentration = buffer.concentration


def build_sample_row(lims: Lims, sample_id: str) -> list:
    sample_row = DebugKapaCSV(SampleID=sample_id)
    sample_row.set_hybridize(hybridize=HybridizeLibraryTWIST(lims=lims, sample_id=sample_id))
    sample_row.set_aliquot(
        aliquot=AliquotsamplesforenzymaticfragmentationTWIST(lims=lims, sample_id=sample_id)
    )
    sample_row.set_kapa(kapa=KAPALibraryPreparation(lims=lims, sample_id=sample_id))
    sample_row.set_pool(pool=PoolsamplesforhybridizationTWIST(lims=lims, sample_id=sample_id))
    sample_row.set_capture(capture=CaptureandWashTWIST(lims=lims, sample_id=sample_id))
    sample_row.set_bead(bead=BeadPurificationTWIST(lims=lims, sample_id=sample_id))
    sample_row.set_buffer(buffer=BufferExchange(lims=lims, sample_id=sample_id))

    sample_row_dict = sample_row.dict(by_alias=True)
    return [sample_row_dict.get(header) for header in HEADERS]


@click.command()
@click.option("--config")
@click.option("--sample_file")
def build_csv(config: str, sample_file: str):
    with open(config) as file:
        config_data = yaml.load(file, Loader=yaml.FullLoader)
    lims = Lims(config_data["BASEURI"], config_data["USERNAME"], config_data["PASSWORD"])

    with open(sample_file, "r") as samples:
        sample_list = [sample_id.strip("\n") for sample_id in samples.readlines()]

    with open("twist.csv", "w", newline="\n") as new_csv:
        wr = csv.writer(new_csv, delimiter=",")
        wr.writerow(HEADERS)
        sample_rows: List[List[str]] = [
            build_sample_row(lims, sample_id) for sample_id in sample_list
        ]
        wr.writerows(sample_rows)


if __name__ == "__main__":
    build_csv()
