# from typing import Any, List

from fastapi import APIRouter, Depends
from cg_lims.app.build.sample import build_sample

from starlette.requests import Request
from starlette.responses import Response


from cg_lims.app import schemas

router = APIRouter()


@router.get("/{sample_id}", response_model=schemas.Sample)
def get_sample(sample_id: str):
    """
    get sample
    """

    # sample = build_sample(sample_id)

    return {"id": sample_id}
