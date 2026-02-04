from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import tracks, analysis, mixer

app = FastAPI(
    title="DJ Mixing Platform API",
    description="Backend API for web-based DJ mixing platform",
    version="1.0.0"
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
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "dj-mixing-backend",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "DJ Mixing Platform API",
        "docs": "/docs",
        "health": "/health"
    }
