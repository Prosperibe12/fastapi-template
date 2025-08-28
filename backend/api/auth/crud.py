from fastapi import Depends, HTTPException, status
from loguru import logger
from sqlmodel import select
from sqlalchemy.ext.asyncio.session import AsyncSession

from backend.models.tables import User
from backend.models.db import DbSession
from backend.api.auth.schema import RegisterSchema, UserResponse
from backend.core.custom_exceptions import ServiceError
from backend.core.security import AccessTokenBearer, get_password_hash

class UserService:
    """
    Service class for user-related operations.
    """
    @staticmethod
    async def get_user_by_email(session: AsyncSession, email: str):
        """
        Retrieve a user by their email address.
        """
        try:
            statement = select(User).where(User.email == email)
            result = await session.execute(statement)
            user = result.scalars().first()
            return user
        except Exception as e:
            logger.error(f"Error retrieving user by email {email}: {e}")

            raise ServiceError(
                message=f"Database error occurred while retrieving user: {email}",
                email=email
            ) from e

    @staticmethod
    async def user_exist(session: AsyncSession, email: str):
        """
        check if a user exists by their email address.
        """
        user = await UserService.get_user_by_email(session, email)
        return True if user is not None else False

    @staticmethod
    async def create_user(session: AsyncSession, request: RegisterSchema):
        """
        create a new user in the database.
        """
        hashed_pwd = get_password_hash(request.password)
        user_data = request.model_dump()
        user_data['hashed_password'] = hashed_pwd
        user_obj = User(
            **user_data
        )
        try:
            session.add(user_obj)
            await session.commit()
            await session.refresh(user_obj)
            return user_obj

        except Exception as e:
            logger.error(f"Error creating user: {request.email} - {e}")

            await session.rollback()

            raise ServiceError(
                message=f"Error creating user: {request.email}",
                email=request.email
            ) from e

    @staticmethod
    async def update_user(user: User, user_data: dict, session: AsyncSession):
        """
        Verify a user by their email address.
        """
        for k, v in user_data.items():
            setattr(user, k, v)

        try:
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

        except Exception as e:
            logger.error(f"Error verifying user: {user.email} - {e}")

            raise ServiceError(
                message=f"Error verifying user: {user.email}",
                email=user.email
            ) from e

async def get_current_user(
    session: DbSession,
    auth_class: dict = Depends(AccessTokenBearer())
):
    """ 
    Dependency to get the current loggedin user.
    """
    user_email = auth_class.get("sub")
    user = await UserService.get_user_by_email(session, user_email)

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    return UserResponse.model_validate(user)
