import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    db_user = os.getenv("POSTGRES_USER", "scraper_user")
    db_pass = os.getenv("POSTGRES_PASSWORD", "change_this_to_a_strong_password")
    db_name = os.getenv("POSTGRES_DB", "scraper_db")
    DATABASE_URL = f"postgresql+asyncpg://{db_user}:{db_pass}@localhost:5432/{db_name}"

# Create async database engine
engine = create_async_engine(DATABASE_URL, echo=False)

# Session factory for creating AsyncSession instances
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Declarative base class for models
Base = declarative_base()

# Dependency provider for FastAPI routes
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
