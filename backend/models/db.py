from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlmodel import create_engine
from sqlmodel import Session

from ..core.config import settings

# define the database engine
engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

def get_db() -> Generator[Session, None, None]:
   """
   Dependency to get a database session.
   """
   with Session(engine) as session:
      yield session

# annotate the generator for better type hinting
DbSession = Annotated[Session, Depends(get_db)]