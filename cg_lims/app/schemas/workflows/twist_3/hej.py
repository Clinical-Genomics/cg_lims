from typing import Optional
from pydantic import BaseModel, Field


class HybridizeLibraryTWIST(BaseModel):
    """Hybridize Library TWIST v2"""

    bait_set: Optional[float] = Field(None, alias="Bait Set")
    capture_kit: Optional[float] = Field(None, alias="Capture kit lot nr.")
    container_name: Optional[float] = Field(None, alias="Container Name")


class HejLibraryTWIST(BaseModel):
    """Hybridize Library TWIST v2"""

    bait_set: Optional[float] = Field(None, alias="Bait Set")
    capture_kit: Optional[float] = Field(None, alias="Capture kit lot nr.")
    container_name: Optional[float] = Field(None, alias="Container Name")


class TwistData(BaseModel):
    sample_id: str = Field(..., alias="SampleID")
    sample_name: str = Field(..., alias="SampleName")
    hyb_bait_set: float = Field(None, alias="HybridizeBaitSet")
    hyb_capture_kit: float = Field(None, alias="HybridizeCaptureKit")
    hyb_container_name: float = Field(None, alias="HybridizeContainerName")
    hej_bait_set: float = Field(None, alias="HejBaitSet")
    hej_capture_kit: float = Field(None, alias="HejCaptureKit")
    hej_container_name: float = Field(None, alias="HejContainerName")

    class Config:
        arbitrary_types_allowed = True

    def set_hybridize(self, hybridize: HybridizeLibraryTWIST):
        self.hyb_bait_set = hybridize.bait_set
        self.hyb_capture_kit = hybridize.capture_kit
        self.hyb_container_name = hybridize.container_name

    def set_hej(self, hej: HejLibraryTWIST):
        self.hej_bait_set = hej.bait_set
        self.hej_capture_kit = hej.capture_kit
        self.hej_container_name = hej.container_name


def build_twist() -> TwistData:
    hyb_values = {"Bait Set": 0.5, "Capture kit lot nr.": 0.1, "Container Name": 0.3}
    hyb = HybridizeLibraryTWIST(**hyb_values)
    hej = HejLibraryTWIST(**hyb_values)
    sample_values = {"SampleID": "sample", "SampleName": "hello"}
    twist_data = TwistData(**sample_values)
    twist_data.set_hybridize(hybridize=hyb)
    twist_data.set_hej(hej=hej)
    return twist_data


csv_header = [
    "SampleID",
    "SampleName",
    "HybridizeBaitSet",
    "HybridizeCaptureKit",
    "HybridizeContainerName",
    "HejBaitSet",
    "HejCaptureKit",
    "HejContainerName",
]
if __name__ == "__main__":
    twist_sample: TwistData = build_twist()
    print("\t".join(csv_header))
    print("\t".join([str(value) for value in twist_sample.dict().values()]))
