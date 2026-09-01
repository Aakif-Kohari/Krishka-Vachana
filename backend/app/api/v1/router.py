from fastapi import APIRouter

from app.api.v1 import crops, farmers, health

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(farmers.router)
api_router.include_router(crops.router)
