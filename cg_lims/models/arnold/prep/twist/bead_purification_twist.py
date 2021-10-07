from typing import Optional

from genologics.lims import Lims
from pydantic import Field, BaseModel
from cg_lims.objects import BaseAnalyte


class BeadPurificationArtifactUDFs(BaseModel):
    bead_purification_size_bp: str = Field(..., alias="Size (bp)")
    bead_purification_concentration: str = Field(..., alias="Concentration")


class BeadPurificationposthybTwistProcessUDFs(BaseModel):
    lot_nr_enrichment_kit_hybridization: str = Field(..., alias="Twist Enrichment Kit")
    lot_nr_etoh_bead_purification_post_hyb: str = Field(..., alias="Ethanol")
    lot_nr_h2o_bead_purification_post_hyb: str = Field(..., alias="Nuclease free water")
    bead_purification_post_hyb_method: str = Field(..., alias="Method document")


class BeadPurificationUDFs(BeadPurificationArtifactUDFs):
    bead_purification_post_hyb_well_position: Optional[str] = Field(None, alias="well_position")
    bead_purification_post_hyb_container_name: Optional[str] = Field(None, alias="container_name")

    class Config:
        allow_population_by_field_name = True


def get_bead_purification_twist(lims: Lims, sample_id: str) -> BeadPurificationUDFs:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        artifact_udf_model=BeadPurificationArtifactUDFs,
        process_type="Bead Purification TWIST v2",
    )

    return BeadPurificationUDFs(
        **analyte.merge_analyte_fields(),
    )
