from pydantic import BaseModel, EmailStr, Field

class RegisterSchema(BaseModel):
   """
   Schema for user registration.
   validate the data provided during user registration.
   """
   email: EmailStr
   full_name: str
   password: str
