from fastapi import APIRouter

from .auth.route import auth_router
from .users.route import user_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(user_router)
