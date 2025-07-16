from fastapi import APIRouter

from backend.api.auth.route import auth_router

# Add all API routers here (Allows for easy management of routes)
api_router = APIRouter()
api_router.include_router(auth_router)
