import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.core.config import settings
from app.core.base_models import Base

logger = logging.getLogger(__name__)

# Async Engine for FastAPI route handlers
db_url = settings.get_database_url

# SQLite connection args for async
connect_args = {}
if "sqlite" in db_url:
    connect_args = {"check_same_thread": False}

async_engine = create_async_engine(
    db_url,
    echo=False,
    connect_args=connect_args,
    pool_pre_ping=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Synchronous Engine for Alembic migrations, Celery tasks, and initial table creation
sync_db_url = settings.get_sync_database_url
sync_connect_args = {}
if "sqlite" in sync_db_url:
    sync_connect_args = {"check_same_thread": False}

sync_engine = create_engine(
    sync_db_url,
    echo=False,
    connect_args=sync_connect_args,
    pool_pre_ping=True
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False
)


async def init_db() -> None:
    """Initialize database tables asynchronously"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables verified / initialized successfully.")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for obtaining async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
