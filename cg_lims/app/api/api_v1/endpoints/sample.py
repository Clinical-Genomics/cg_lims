from fastapi import APIRouter, Depends
from cg_lims.app.api.deps import get_lims
from cg_lims.models.api import Sample

from genologics.lims import Lims
from genologics.entities import Sample as GenologicsSample


router = APIRouter()


@router.get("/{sample_id}", response_model=Sample)
def get_sample(sample_id: str, lims: Lims = Depends(get_lims)):
    """get sample"""
    sample = GenologicsSample(lims, id=sample_id)
    sample_udfs = dict(sample.udf.items())
    return Sample(**sample_udfs, id=sample.id, name=sample.name, project=sample.project.id)
