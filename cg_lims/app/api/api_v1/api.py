from fastapi import APIRouter

from app.api.api_v1.endpoints import sample

api_router = APIRouter()
api_router.include_router(sample.router, prefix="/sample", tags=["sample"])
