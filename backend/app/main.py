from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import check_database_connection, create_tables
from app.api import tracks, analysis, mixer
import logging
import redis
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown event handler"""
    # Startup
    logger.info("Starting DJ Mixing Platform API...")
    
    # Check database connection
    logger.info("Checking database connection...")
    if not check_database_connection(max_retries=10, retry_delay=3):
        logger.error("Failed to connect to database. Application may not work correctly.")
    else:
        # Create tables if they don't exist
        try:
            create_tables()
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
    
    # Check Redis connection
    logger.info("Checking Redis connection...")
    try:
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        redis_client.ping()
        logger.info("Redis connection successful")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}. Caching will not be available.")
    
    # Check upload directory
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    logger.info(f"Upload directory ready: {settings.UPLOAD_DIR}")
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down DJ Mixing Platform API...")

app = FastAPI(
    title="DJ Mixing Platform API",
    description="Backend API for web-based DJ mixing platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tracks.router, prefix="/api/tracks", tags=["tracks"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(mixer.router, prefix="/api/mixer", tags=["mixer"])

@app.get("/health")
async def health_check():
    """Health check endpoint with service status"""
    status = {
        "status": "healthy",
        "service": "dj-mixing-backend",
        "version": "1.0.0",
        "database": "unknown",
        "redis": "unknown"
    }
    
    # Check database
    try:
        from app.core.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        status["database"] = "connected"
    except Exception as e:
        status["database"] = f"error: {str(e)}"
        status["status"] = "degraded"
    
    # Check Redis
    try:
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        redis_client.ping()
        status["redis"] = "connected"
    except Exception as e:
        status["redis"] = f"error: {str(e)}"
        status["status"] = "degraded"
    
    return status

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "DJ Mixing Platform API",
        "docs": "/docs",
        "health": "/health"
    }
