from genologics.lims import Lims
from pydantic import Field, BaseModel
from cg_lims.objects import BaseAnalyte
from cg_lims.models.arnold.prep.base_step import BaseStep


class BeadPurificationArtifactUDFs(BaseModel):
    bead_purification_size_bp: int = Field(..., alias="Size (bp)")
    bead_purification_concentration: float = Field(..., alias="Concentration")


class BeadPurificationProcessUDFs(BaseModel):
    lot_nr_enrichment_kit_hybridization: str = Field(..., alias="Twist Enrichment Kit")
    lot_nr_etoh_bead_purification_post_hyb: str = Field(..., alias="Ethanol")
    lot_nr_h2o_bead_purification_post_hyb: str = Field(..., alias="Nuclease free water")
    bead_purification_post_hyb_method: str = Field(..., alias="Method document")


class BeadPurificationFields(BaseStep):
    artifact_udfs: BeadPurificationArtifactUDFs
    process_udfs: BeadPurificationProcessUDFs

    class Config:
        allow_population_by_field_name = True


def get_bead_purification_twist(lims: Lims, sample_id: str, prep_id: str) -> BeadPurificationFields:
    analyte = BaseAnalyte(
        lims=lims,
        sample_id=sample_id,
        process_type="Bead Purification TWIST v2",
    )

    return BeadPurificationFields(
        **analyte.base_fields(),
        process_udfs=BeadPurificationProcessUDFs(**analyte.process_udfs()),
        artifact_udfs=BeadPurificationArtifactUDFs(**analyte.artifact_udfs()),
        sample_id=sample_id,
        prep_id=prep_id,
        step_type="bead_purification",
        workflow="TWIST",
    )
