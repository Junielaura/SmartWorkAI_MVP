from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import ensure_directories, settings
from app.api.v1.router import api_v1_router
from app.api.v1.documents import router as documents_router
from app.api.v1.generation import router as generation_router
from app.api.v1.analytics import api_v1_router as analytics_router
from app.api.v1.chat import router as chat_router
from app.api.v1.reporting import router as reporting_router
from app.api.v1.tasks import router as tasks_router

@asynccontextmanager
def lifespan(app: FastAPI):
    ensure_directories()
    yield


app = FastAPI(
    title="SmartWork AI MVP",
    description="Plateforme intelligente d'automatisation documentaire et de production de livrables professionnels",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware - configure for production origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router (auth)
app.include_router(api_v1_router, prefix="/api/v1")

# Include documents router
app.include_router(documents_router, prefix="/api/v1")

# Include generation router
app.include_router(generation_router, prefix="/api/v1")

# Include analytics router
app.include_router(analytics_router, prefix="/api/v1")

# Include reporting router
app.include_router(reporting_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")

# Include chat router
app.include_router(chat_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "SmartWork AI MVP", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}