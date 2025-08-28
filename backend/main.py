import sentry_sdk
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from .api.app import api_router
from .core.config import settings
from .core.logger import setup_logging
from .core.handlers import register_custom_errors
from .core.middleware import register_middleware

# initialize logging
setup_logging()

# initialize Sentry for error tracking
if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    openapi_url=f"{settings.API_VERSION}/openapi.json",
)

# register custom errors
register_custom_errors(app)

# add server error exception handler
app.exception_handler(500)
async def server_error_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Oops! Something went wrong on the server."},
    )

# set middleware and CORS
register_middleware(app)

if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# health check endpoint
@app.get("/")
async def health_check():
    """
    Application health check endpoint.
    """
    return {"message": "Hello, World!"}

app.include_router(api_router, prefix=settings.API_VERSION)
