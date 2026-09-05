"""API v1 router aggregating all endpoint modules."""
from fastapi import APIRouter

from app.api.v1 import bookings, centres, crops, farmers, health, queue, payments, cluster

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(farmers.router)
api_router.include_router(crops.router)
api_router.include_router(centres.router)
api_router.include_router(bookings.router)
api_router.include_router(queue.router)
api_router.include_router(payments.router)
api_router.include_router(cluster.router)
