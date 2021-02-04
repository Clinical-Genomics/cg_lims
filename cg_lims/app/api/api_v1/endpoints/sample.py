from typing import Any, List

from fastapi import APIRouter, Depends
from starlette.requests import Request

from app import models, schemas
from app.api import deps

router = APIRouter()


@router.get("/samples/{sample_id}", )
def get_sample(sample_id, request: Request):
    """
    get sample
    """
    build_sample

    sample=
    return sample