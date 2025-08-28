import json
from typing import Any
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, status

from backend.models.db import DbSession
from backend.core.custom_exceptions import UserAlreadyExists, URLTokenError
from backend.core.security import (
    blacklist_token, decode_url_token, verify_password,
    create_access_token, get_password_hash,
    RefreshTokenBearer
)
from backend.jobs import tasks
from backend.core.response import CustomResponse
from .crud import UserService as crud
from .schema import (
	PasswordConfirmSchema,
	RegisterSchema,
    UserLogin,
    UserData,
    UserLoginResponse,
    ResetPasswordSchema
)

auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@auth_router.post("/register/", status_code=status.HTTP_201_CREATED)
async def register(request: RegisterSchema, session: DbSession) -> Any:
    """
    This endpoint creates a new user account.
    Validates the user registration data, checks if email exists, 
    creates a new user record, and dispatches an email verification message.
    """
    user_exist = await crud.user_exist(session, request.email)

    if user_exist:
        raise UserAlreadyExists()

    new_user = await crud.create_user(session, request)

    if new_user:
        # dispatch email verification
        tasks.send_register_email.delay(
            json.dumps(
                {
                    "id": str(new_user.id), 
                    "email": new_user.email, 
                    "full_name": new_user.full_name
                }
            )
        )

        return CustomResponse.success(
            "User created successfully",
            status_code=status.HTTP_201_CREATED
        )

@auth_router.get("/verify/{token}", status_code=status.HTTP_200_OK)
async def verify(token: str, session: DbSession) -> Any:
    """
    Verify user email endpoint, decode token, set user as verified.
    If token is invalid, raises URLTokenError.
    """ 
    try:
        decoded_token = decode_url_token(token)
        user_obj = await crud.get_user_by_email(session, decoded_token["email"])

        if user_obj is not None:
            await crud.update_user(user_obj, {"is_verified": True}, session)

            return CustomResponse.success(
                "User Verification succesful",
                status_code=status.HTTP_200_OK
            )

        return CustomResponse.failure("User not found", status_code=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        raise URLTokenError()

@auth_router.post("/login/", status_code=status.HTTP_200_OK)
async def login(request: UserLogin, session: DbSession) -> Any:
    """
    Authenticates a user credentials and returns an access token if successful.
    """
    user = await crud.get_user_by_email(session, request.email)

    if not user.is_verified:
        return CustomResponse.failure(
            "User is not verified. Please check your email for verification link.",
            status_code=status.HTTP_403_FORBIDDEN
        )

    if user is not None and verify_password(request.password, user.hashed_password):
        access_token = create_access_token(data={"sub": str(user.email)})
        refresh_token = create_access_token(data={"sub": str(user.email)},
                                            exp=timedelta(days=2), refresh=True)

        response = UserLoginResponse(
            user=UserData(
                id=str(user.id),
                email=user.email,
                full_name=user.full_name,
                is_verified=user.is_verified
            ),
            access_token=access_token,
            refresh_token=refresh_token
        )

        return CustomResponse.success(
            response.model_dump(),
            status_code=status.HTTP_200_OK
        )

    return CustomResponse.failure(
        "Invalid Email or Password", 
        status_code=status.HTTP_403_FORBIDDEN
    )

@auth_router.post("/password-reset-request/", status_code=status.HTTP_202_ACCEPTED)
async def reset_password(request: ResetPasswordSchema, session: DbSession) -> Any:
    """
    Reset user password endpoint.
    Validates user credentials and sends a reset password email.
    """
    user = await crud.get_user_by_email(session, request.email)

    if user is None:
        return CustomResponse.failure(
            "User with this email does not exist.",
            status_code=status.HTTP_404_NOT_FOUND
        )

    # send reset password email
    tasks.send_reset_password_email.delay(
        json.dumps(
            {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name
            }
        )
    )
    return CustomResponse.success(
        "Reset password email sent successfully.",
        status_code=status.HTTP_202_ACCEPTED
    )

@auth_router.post("/password-reset-confirm/{token}", status_code=status.HTTP_200_OK)
async def reset_password_confirm(token: str, request: PasswordConfirmSchema, session: DbSession) -> Any:
    """
    Confirm password reset endpoint \n
    Decode and validate token and update the user's password.
    """
    try:
        if request.password != request.confirm_password:
            return CustomResponse.failure(
                "Passwords do not match.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        decoded_token = decode_url_token(token)
        user = await crud.get_user_by_email(session, decoded_token["email"])

        if user is None:
            return CustomResponse.failure(
                "User with this email does not exist.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        # update password
        hashed_pwd = get_password_hash(request.password)
        await crud.update_user(user, {"hashed_password": hashed_pwd}, session)

        return CustomResponse.success("Password Reset Successful.", status_code=status.HTTP_200_OK)

    except Exception as e:
        raise URLTokenError() from e

@auth_router.post("/refresh-token/", status_code=status.HTTP_200_OK)
async def refresh_token(auth_class = Depends(RefreshTokenBearer())) -> Any:
    """
    Refresh token endpoint.
    Create a new access token using a valid refresh token.
    """
    print("Auth class", auth_class)
    expiry_timestamp = auth_class["exp"]
    expiry = datetime.fromtimestamp(expiry_timestamp, tz=timezone.utc)

    if expiry > datetime.now(timezone.utc):
        access_token = create_access_token(data={"sub": str(auth_class["sub"])})

        return CustomResponse.success(
            {"access_token": access_token},
            status_code=status.HTTP_200_OK
        )

    return CustomResponse.failure(
        "Refresh token has expired.",
        status_code=status.HTTP_403_FORBIDDEN
    )

@auth_router.post("/logout/")
async def logout(auth_class = Depends(RefreshTokenBearer())) -> Any:
    """
    Logout Endpoint.    
    Since access tokens are shortlived(3hrs), it makes more sense to 
    blacklist the refresh token to prevent further token refreshes.
    """
    token = auth_class["jti"]
    await blacklist_token(token)

    return CustomResponse.success(
        "Logout successful.",
        status_code=status.HTTP_200_OK
    )
