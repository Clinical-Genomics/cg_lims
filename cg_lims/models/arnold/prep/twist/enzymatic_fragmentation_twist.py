from typing import Optional

from genologics.lims import Lims
from pydantic import Field, BaseModel

from cg_lims.objects import BaseAnalyte


class EnzymaticFragmentationTWISTProcessUdfs(BaseModel):
    fragmentation_method: Optional[str] = Field(None, alias="Method document")
    fragmentation_time: Optional[float] = Field(None, alias="Fragmentation time (min)")
    fragmentation_kit: Optional[str] = Field(None, alias="KAPA HyperPlus Kit")
    fragmentation_instrument_hybridization: Optional[str] = Field(None, alias="Thermal cycler name")


class EnzymaticFragmentationTWISTUdfs(EnzymaticFragmentationTWISTProcessUdfs):
    fragmentation_well_position: Optional[str] = Field(None, alias="well_position")
    fragmentation_container_name: Optional[str] = Field(None, alias="container_name")

    class Config:
        allow_population_by_field_name = True


def get_enzymatic_fragmentation(lims: Lims, sample_id: str) -> EnzymaticFragmentationTWISTUdfs:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_udf_model=EnzymaticFragmentationTWISTProcessUdfs,
        process_type="Enzymatic fragmentation TWIST v2",
        optional_step=True,
    )

    return EnzymaticFragmentationTWISTUdfs(
        **analyte.merge_analyte_fields(),
    )
