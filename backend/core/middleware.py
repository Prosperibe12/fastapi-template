import time
import logging

from loguru import logger as loguru_logger
from fastapi import FastAPI
from fastapi.requests import Request

logger = logging.getLogger(__name__)
logger.disabled = True

def register_middleware(app: FastAPI):
    """ 
    Register custom middleware for tracking request processing time.
    """
    @app.middleware("http")
    async def custom_logging_middleware(request: Request, call_next):
        
        start_time = time.time()
        
        response = await call_next(request)
        processing_time = time.time() - start_time
                
        # log response with different levels based on status/time
        if response.status_code >= 500:
            loguru_logger.error(
                f"{request.client.host} - {request.method} {request.url.path} - {response.status_code} - {processing_time:.4f}s"
            )
        elif response.status_code >= 400:
            loguru_logger.warning(
                f"{request.client.host} - {request.method} {request.url.path} - {response.status_code} - {processing_time:.4f}s"
            )
        elif processing_time > 1.0:  # Slow requests
            loguru_logger.warning(
                f"Slow request: {request.client.host} - {request.method} {request.url.path} - {response.status_code} - {processing_time:.4f}s"
            )
        else:
            loguru_logger.info(
                f"{request.client.host} - {request.method} {request.url.path} - {response.status_code} - {processing_time:.4f}s"
            )
        return response