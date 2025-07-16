import uuid
from datetime import datetime

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime, func

class User(SQLModel, table=True):
   id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
   email: str = Field(unique=True, nullable=False, max_length=255)
   full_name: str = Field(nullable=False, max_length=255)
   hashed_password: str = Field(nullable=False)
   is_verified: bool = Field(default=False)
   is_active: bool = Field(default=False)
   is_superuser: bool = Field(default=False)
   created_at: datetime = Field(
      sa_column=Column(DateTime(timezone=True), server_default=func.now())
   )
   updated_at: datetime = Field(
      sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
   )
