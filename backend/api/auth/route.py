from typing import Any

from fastapi import APIRouter, status, HTTPException
from fastapi.responses import JSONResponse

from .schema import (
	RegisterSchema
)
from . import crud
from ...models.db import DbSession


auth_router = APIRouter(
	prefix="/auth",
	tags=["Authentication"],
)

@auth_router.post("/register/", status_code=status.HTTP_201_CREATED)
async def register(session: DbSession, request: RegisterSchema) -> Any:
	"""
	This endpoint allows a new user registration.
	"""
	# validate the request data with the schema
	if request.model_validate(request, strict=True):
		
		# check if the user already exists
		user = await crud.get_user_by_email(session, request.email)
		if user:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="User with this email already exists."
			)
		# create a new user 
		new_user = await crud.create_user(session, request)
		# send email verification email
		return JSONResponse(
			status_code=status.HTTP_201_CREATED,
			content={"message": "User registered successfully."}
		)
     