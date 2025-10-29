"""API v1 router"""

from fastapi import APIRouter
from app.api.v1.endpoints import health, upload, parse, pipeline, features

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(upload.router, tags=["Upload"])
api_router.include_router(parse.router, tags=["Parse"])
api_router.include_router(pipeline.router, prefix="/pipeline", tags=["Pipeline"])
api_router.include_router(features.router, tags=["Features"])

