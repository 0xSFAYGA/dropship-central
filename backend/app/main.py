
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.core.redis import connect_redis, close_redis
from app.core.logging import configure_logging, logger
from app.api.v1.router import api_router

# Configure structured logging
configure_logging()

app = FastAPI(
    title="Dropship Central API",
    version="1.0.0-mvp",
    description="Multi-marketplace dropshipping automation SaaS",
)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up...")
    await connect_redis()
    logger.info("Redis connected.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down...")
    await close_redis()
    logger.info("Redis disconnected.")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Generic Exception Handler
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """
    Catch all exceptions and return a JSON response.
    """
    logger.error(f"An unexpected error occurred: {exc}")
    return JSONResponse(
        status_code=500,
        content={"status": "error", "detail": "An internal server error occurred."},
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["General"])
async def read_root():
    """
    Root endpoint providing basic API information.
    """
    return {"message": "Dropship Central API", "version": "1.0.0-mvp"}

@app.get("/health", tags=["General"])
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok"}

logger.info("Dropship Central API starting up...")
