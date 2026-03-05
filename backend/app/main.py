
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import select
from backend.app.core.config import settings
from backend.app.core.database import init_db, AsyncSessionLocal
from backend.app.api.routes import auth, images, captions, albums, dashboard, admin, pages
from backend.app.api.routes import settings as settings_router 
from fastapi.staticfiles import StaticFiles
import os
import logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        logger.info("[STARTUP] Initializing database...")
        await init_db()
        logger.info("[STARTUP] Database initialized successfully")
    except Exception as e:
        logger.error(f"[STARTUP] Database initialization failed: {e}", exc_info=True)
        # Don't crash the app if DB init fails during startup
    yield
    # Shutdown

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Mount uploads directory so image files saved under `settings.UPLOAD_DIR` are served
uploads_dir = settings.UPLOAD_DIR
# Ensure absolute path
if not os.path.isabs(uploads_dir):
    uploads_dir = os.path.abspath(os.path.join(os.getcwd(), uploads_dir))
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")
print(f"[STARTUP] Mounted uploads directory: {uploads_dir}")

# Mount static files (CSS, JS) for templates
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# API routes
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(images.router, prefix=f"{settings.API_V1_STR}/images", tags=["images"])
app.include_router(captions.router, prefix=f"{settings.API_V1_STR}/captions", tags=["captions"])
app.include_router(albums.router, prefix=f"{settings.API_V1_STR}/albums", tags=["albums"])
app.include_router(dashboard.router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["dashboard"])
app.include_router(admin.router, prefix=f"{settings.API_V1_STR}/admin", tags=["admin"])
app.include_router(settings_router.router, prefix=f"{settings.API_V1_STR}/settings", tags=["settings"])

# Page routes (server-side rendered templates) – must come AFTER static mounts
app.include_router(pages.router, tags=["pages"])

# Health check endpoint
@app.get(f"{settings.API_V1_STR}/health", tags=["health"])
async def health_check():
    """Health check endpoint for container orchestration."""
    health_info = {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "upload_dir": settings.UPLOAD_DIR,
        "upload_dir_exists": os.path.exists(settings.UPLOAD_DIR)
    }
    
    # Check if we can access the database
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(select(1))
            health_info["database"] = "ok"
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
        health_info["database"] = f"error: {str(e)}"
    
    return health_info
