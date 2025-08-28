from typing import Any

from fastapi import APIRouter, Depends

from backend.api.auth.crud import get_current_user

user_router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

@user_router.get("/user/")
async def get_user(user: dict = Depends(get_current_user)) -> Any:
    """
    Retrieve the current logged in user details.
    """
    return user
