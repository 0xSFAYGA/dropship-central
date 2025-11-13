import logging
from typing import AsyncGenerator, Tuple

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy import text

from backend.app.config import get_settings

# Initialize logger for this module
logger = logging.getLogger(__name__)


async def create_engine() -> AsyncEngine:
    """
    Creates and returns an asynchronous SQLAlchemy engine.

    Loads database URL and other settings from the application configuration.
    Configures connection pooling and pre-ping for production readiness.

    Returns:
        AsyncEngine: The created SQLAlchemy asynchronous engine.

    Raises:
        Exception: If there is an error creating the database engine.
    """
    settings = get_settings()
    try:
        engine = create_async_engine(
            settings.DATABASE_URL,
            pool_min_size=settings.DB_POOL_MIN_SIZE,
            pool_max_size=settings.DB_POOL_MAX_SIZE,
            pool_pre_ping=True,  # Test connections for staleness
            echo=settings.DB_ECHO,  # Log SQL statements if DB_ECHO is True
        )
        logger.info("Database engine created successfully.")
        return engine
    except Exception as e:
        logger.error(f"Failed to create database engine: {e}", exc_info=True)
        raise


def get_async_session_maker(engine: AsyncEngine):
    """
    Creates and returns an asynchronous sessionmaker.

    Args:
        engine (AsyncEngine): The SQLAlchemy asynchronous engine.

    Returns:
        async_sessionmaker: A factory for creating new AsyncSession instances.
    """
    async_session_maker = async_sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,  # Important for async operations
    )
    logger.info("Async session maker created.")
    return async_session_maker


async def get_db(async_session_maker) -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides an asynchronous database session.

    Yields:
        AsyncSession: A new asynchronous database session.
    """
    session: AsyncSession = async_session_maker()
    try:
        yield session
    except Exception as e:
        logger.error(f"Database session error: {e}", exc_info=True)
        await session.rollback()
        raise
    finally:
        await session.close()


async def init_db() -> Tuple[AsyncEngine, async_sessionmaker]:
    """
    Initializes the database engine and session maker.

    This function should be called during application startup.
    It also tests the database connection.

    Returns:
        Tuple[AsyncEngine, async_sessionmaker]: The initialized engine and session maker.

    Raises:
        Exception: If database initialization or connection test fails.
    """
    logger.info("Initializing database...")
    engine = await create_engine()
    async_session_maker = get_async_session_maker(engine)
    try:
        # Test the database connection
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        logger.info("✅ DB initialized and connection tested.")
        return engine, async_session_maker
    except Exception as e:
        logger.critical(
            "❌ Failed to initialize database or test connection: %s", e, exc_info=True
        )
        await engine.dispose()
        raise


async def close_db(engine: AsyncEngine):
    """
    Closes the database connection pool.

    This function should be called during application shutdown.

    Args:
        engine (AsyncEngine): The SQLAlchemy asynchronous engine to dispose.
    """
    logger.info("Closing database connections...")
    if engine:
        await engine.dispose()
        logger.info("✅ Database connections closed.")
    else:
        logger.warning("Attempted to close database, but engine was not initialized.")
