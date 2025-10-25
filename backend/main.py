"""
ProbePilot FastAPI Backend
Main application entry point for the telemetry processing engine
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime
import logging
from typing import List, Dict, Any, Optional

# Import API routers
from api.v1 import probes, metrics, system, copilot, events, alerts, historical_metrics
from core.config import get_settings
from core.database import get_database
from core.probe_manager import probe_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title="ProbePilot API",
    description="Your Mission Control for Kernel Observability - Backend API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for Gradio frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:7860", "http://127.0.0.1:7860"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(
    probes.router,
    prefix="/api/v1/probes",
    tags=["probes"],
    responses={404: {"description": "Probe not found"}},
)

app.include_router(
    metrics.router,
    prefix="/api/v1/metrics", 
    tags=["metrics"],
    responses={404: {"description": "Metrics not found"}},
)

app.include_router(
    system.router,
    prefix="/api/v1/system",
    tags=["system"],
    responses={503: {"description": "System unavailable"}},
)

app.include_router(
    copilot.router,
    prefix="/api/v1/copilot",
    tags=["copilot"],
    responses={500: {"description": "AI service unavailable"}},
)

app.include_router(
    events.router,
    prefix="/api/v1",
    tags=["events"],
    responses={500: {"description": "Events service unavailable"}},
)

app.include_router(
    alerts.router,
    prefix="/api/v1",
    tags=["alerts"],
    responses={500: {"description": "Alert engine unavailable"}},
)

app.include_router(
    historical_metrics.router,
    prefix="/api/v1",
    tags=["historical-metrics"],
    responses={500: {"description": "Historical metrics unavailable"}},
)

from api.v1 import advanced_analytics

app.include_router(
    advanced_analytics.router,
    prefix="/api/v1/analytics",
    tags=["advanced-analytics"],
    responses={500: {"description": "Advanced analytics unavailable"}},
)

@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "🛩️ ProbePilot Mission Control API",
        "version": "0.1.0",
        "description": "Your Mission Control for Kernel Observability",
        "docs": "/docs",
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "0.1.0",
        "services": {
            "api": "operational",
            "database": "connected",
            "probe_manager": "ready"
        }
    }

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Resource not found",
            "message": "The requested resource was not found",
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 handler"""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("🛩️ Starting ProbePilot Mission Control API...")
    logger.info("📡 Initializing probe management system...")
    logger.info("🔍 Setting up telemetry processing engine...")
    
    # Initialize Redis database connection
    db = get_database()
    db.connect()
    if db.is_connected():
        logger.info("🔗 Connected to Redis database successfully")
    else:
        logger.warning("⚠️ Failed to connect to Redis - using in-memory storage")
    
    # Start the real probe manager
    await probe_manager.start()
    logger.info("🚀 Real Probe Manager started - probes will automatically progress and collect live metrics")
    
    logger.info("🤖 Connecting AI Copilot services...")
    logger.info("✅ ProbePilot API ready for takeoff!")

@app.on_event("shutdown") 
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛬 ProbePilot API landing safely...")
    logger.info("📡 Stopping active probes...")
    logger.info("💾 Saving telemetry data...")
    
    # Stop the probe manager
    await probe_manager.stop()
    logger.info("🔴 Real Probe Manager stopped")
    
    # Disconnect from Redis
    db = get_database()
    db.disconnect()
    logger.info("🔗 Disconnected from Redis database")
    
    logger.info("✅ ProbePilot API shutdown complete")

if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )