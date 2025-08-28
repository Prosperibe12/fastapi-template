from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession

from backend.core.config import settings

# define the database engine
engine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    echo=False,
    future=True
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a database session.
    """
    async_session = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_session() as session:
        yield session

# annotate the generator for better type hinting
DbSession = Annotated[AsyncSession, Depends(get_db)]
