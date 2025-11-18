"""
FastAPI main application for Health Ecosystem Hub Backend
"""

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
import time
import logging
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_database
from app.middleware.auth import AuthMiddleware
from app.middleware.logging import LoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.api import auth, patients, appointments, prescriptions, inventory, orders
from app.utils.exceptions import HealthHubException, setup_exception_handlers
from app.utils.websocket import websocket_manager


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("health_hub.log")
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Health Ecosystem Hub Backend...")
    
    # Initialize database
    db_initialized = await init_database()
    if not db_initialized:
        logger.error("Failed to initialize database")
        raise RuntimeError("Database initialization failed")
    
    logger.info("Database initialized successfully")
    logger.info(f"Application running on {settings.host}:{settings.port}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Health Ecosystem Hub Backend...")
    # Cleanup WebSocket connections
    await websocket_manager.disconnect_all()
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Comprehensive healthcare management system backend API",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Add custom exception handlers
setup_exception_handlers(app)

# Add middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.debug else ["localhost", "127.0.0.1"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuthMiddleware)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to responses"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Include API routers
app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

app.include_router(
    patients.router,
    prefix="/api/v1/patients",
    tags=["Patients"]
)

app.include_router(
    appointments.router,
    prefix="/api/v1/appointments",
    tags=["Appointments"]
)

app.include_router(
    prescriptions.router,
    prefix="/api/v1/prescriptions",
    tags=["Prescriptions"]
)

app.include_router(
    inventory.router,
    prefix="/api/v1/inventory",
    tags=["Inventory"]
)

app.include_router(
    orders.router,
    prefix="/api/v1/orders",
    tags=["Orders"]
)


# Health check endpoints
@app.get("/health", tags=["Health"])
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.app_version
    }


@app.get("/health/detailed", tags=["Health"])
async def detailed_health_check():
    """Detailed health check with system status"""
    try:
        # Check database connection
        from app.database import supabase_client
        db_status = await supabase_client.test_connection()
        
        return {
            "status": "healthy" if db_status else "unhealthy",
            "timestamp": time.time(),
            "version": settings.app_version,
            "database": "connected" if db_status else "disconnected",
            "services": {
                "database": "ok" if db_status else "error",
                "websocket": "ok",
                "middleware": "ok"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unavailable")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Health Ecosystem Hub Backend API",
        "version": settings.app_version,
        "docs": "/docs" if settings.debug else "Documentation not available in production",
        "health": "/health"
    }


@app.get("/api/v1/info", tags=["Info"])
async def api_info():
    """API information"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "Comprehensive healthcare management system backend API",
        "endpoints": {
            "auth": "/api/v1/auth",
            "patients": "/api/v1/patients",
            "appointments": "/api/v1/appointments",
            "prescriptions": "/api/v1/prescriptions",
            "inventory": "/api/v1/inventory",
            "orders": "/api/v1/orders"
        },
        "documentation": "/docs" if settings.debug else "Not available in production"
    }


# WebSocket endpoint
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket, user_id: str):
    """WebSocket endpoint for real-time updates"""
    await websocket_manager.connect(websocket, user_id)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {str(e)}")
    finally:
        await websocket_manager.disconnect(user_id)


# Startup event handler
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("Health Ecosystem Hub Backend starting up...")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Allowed origins: {settings.allowed_origins}")


# Shutdown event handler
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Health Ecosystem Hub Backend shutting down...")


# Global exception handler for unhandled exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error_code": "INTERNAL_ERROR",
            "timestamp": time.time()
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
