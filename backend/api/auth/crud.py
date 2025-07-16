from sqlmodel import Session, select 

from backend.models.tables import User
from backend.api.auth.schema import RegisterSchema
from backend.core.security import get_password_hash

def get_user_by_email(session: Session, email: str):
   """   Retrieve a user by their email address."""
   try:
      # query user from db
      statement = select(User).where(User.email == email)
      result = session.exec(statement).first()
      return result
   except Exception as e:
      message = (f"Error retrieving user by email: {email}. Error: {e}")
      raise Exception(message)

def create_user(session: Session, request: RegisterSchema):
   """Create a new user in the database."""
   
   user_obj = User.model_validate(
      request, update={"hashed_password": get_password_hash(request.password)}
   )
   try:
      session.add(user_obj)
      session.commit()
      session.refresh(user_obj)
      return user_obj
   except Exception as e:
      message = f"Error creating user: {request.email}. Error: {e}"
      raise Exception(message)