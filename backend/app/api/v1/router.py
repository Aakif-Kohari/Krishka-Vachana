from fastapi import APIRouter

from app.api.v1 import bookings, centres, crops, farmers, health, queue

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(farmers.router)
api_router.include_router(crops.router)
api_router.include_router(centres.router)
api_router.include_router(bookings.router)
api_router.include_router(queue.router)
