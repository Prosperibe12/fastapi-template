from typing import Any
from fastapi import responses, status 

class CustomResponse(responses.JSONResponse):
    """
    Application custom response class to standardize API responses.
    """
    @classmethod
    def success(cls, content: Any, status_code: int = status.HTTP_200_OK):
        data = {
            "data": content,
            "message": "Success",
            "errors": [],
            "status_code": status_code
        }
        return cls(content=data, status_code=status_code)

    @classmethod
    def failure(cls, content: Any, status_code: int = status.HTTP_400_BAD_REQUEST):
        data = {
            "data": [],
            "message": "Failed",
            "errors": content,
            "status_code": status_code
        }
        return cls(content=data, status_code=status_code)
