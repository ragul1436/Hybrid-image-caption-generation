
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from backend.app.core.config import settings
from backend.app.models.db_models import Base
import asyncio
import logging

logger = logging.getLogger(__name__)

# Convert standard PostgreSQL URL to asyncpg if needed
database_url = settings.DATABASE_URL
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# Create Async Engine with connect timeout
engine = create_async_engine(
    database_url,
    echo=False,
    future=True,
    poolclass=NullPool,
    connect_args={"timeout": 5},  # 5-second connection timeout
)

# Async Session Maker
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
            
async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.warning(f"Database connection failed: {e}")
        logger.warning("App will start without DB — API calls requiring DB will fail.")
