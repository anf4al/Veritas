import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings, validate_provider_keys
from backend.app.core.database import engine, Base
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.companies import router as companies_router
from backend.app.api.v1.users import router as users_router
from backend.app.api.v1.documents import router as documents_router
from backend.app.api.v1.chat import router as chat_router
from backend.app.api.v1.tools import router as tools_router
from backend.app.api.v1.observability import router as observability_router
from backend.app.api.v1.evaluation import router as evaluation_router
from backend.app.api.v1.provider import router as provider_router
from backend.app.observability.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing database schema...")
    Base.metadata.create_all(bind=engine)

    provider_check = validate_provider_keys()
    logger.info(
        f"AI Provider selected: '{provider_check['provider']}'. "
        f"Key configured: {provider_check['configured']}."
    )
    yield
    # Shutdown
    logger.info("Veritas server shutting down...")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-minded enterprise intelligence and research platform.",
    lifespan=lifespan
)

# Enable CORS for React frontend development and preview
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include v1 Routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(companies_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(tools_router, prefix="/api/v1")
app.include_router(observability_router, prefix="/api/v1")
app.include_router(evaluation_router, prefix="/api/v1")
app.include_router(provider_router, prefix="/api/v1")

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "provider": settings.AI_PROVIDER
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
