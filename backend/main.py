from fastapi import FastAPI

from backend.api.app import api_router
from backend.core.config import settings

app = FastAPI(
	title=settings.APP_NAME,
	description=settings.APP_DESCRIPTION,
	version=settings.APP_VERSION,
	openapi_url=f"{settings.API_VERSION}/openapi.json",
)

@app.get("/")
async def health_check():
	"""
	Application health check endpoint.
	Returns a simple JSON response to indicate the service is running.
	"""
	return {"message": "Hello, World!"}
app.include_router(api_router, prefix=settings.API_VERSION)
