import uuid
from typing import Optional
from datetime import datetime

import sqlalchemy.dialects.postgresql as pg
from sqlalchemy import Column, DateTime, func
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    """User model"""
    __tablename__ = "users"

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            primary_key=True,
            default=uuid.uuid4,
            nullable=False
        )
    )
    email: str = Field(unique=True, nullable=False, max_length=255)
    full_name: str = Field(nullable=False, max_length=255)
    hashed_password: str = Field(nullable=False)
    is_verified: bool = Field(default=False)
    is_active: bool = Field(default=False)
    is_superuser: bool = Field(default=False)
    created_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, is_verified={self.is_verified})>"
