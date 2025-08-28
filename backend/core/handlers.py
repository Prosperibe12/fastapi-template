from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse

from . custom_exceptions import (
    UserAlreadyExists,
    URLTokenError,
    InvalidTokenError,
    BlacklistedTokenError
)

def create_exception_handler(status_code: int, detail: str):
    """custom exception handler """
    def handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status_code,
            content={
                "error_type": exc.__class__.__name__,
                "detail": detail,
                "error": str(exc),
            }
        )
    return handler

def register_custom_errors(app: FastAPI):
    """ custom error handlers  """
    app.add_exception_handler(
        UserAlreadyExists,
        create_exception_handler(
            status.HTTP_400_BAD_REQUEST,
            "This email is already registered.",
        )
    )

    app.add_exception_handler(
        URLTokenError,
        create_exception_handler(
            status.HTTP_400_BAD_REQUEST,
            "Invalid Verification Token",
        )
    )

    app.add_exception_handler(
        InvalidTokenError,
        create_exception_handler(
            status.HTTP_403_FORBIDDEN,
            "Invalid or Expired Token",
        )
    )

    app.add_exception_handler(
        BlacklistedTokenError,
        create_exception_handler(
            status.HTTP_401_UNAUTHORIZED,
            "Token has been revoked",
        )
    )