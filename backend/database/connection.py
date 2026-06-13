from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from typing import Optional
import asyncpg

class DatabaseConnectionFactory:
    _engine: Optional[AsyncEngine] = None
    
    @classmethod
    def get_sqlalchemy_engine(cls, database_url: str) -> AsyncEngine:
        if cls._engine is None:
            # SQLAlchemy asyncpg requires postgresql+asyncpg://
            if not database_url.startswith("postgresql+asyncpg://"):
                database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
            cls._engine = create_async_engine(database_url, echo=False)
        return cls._engine
    
    @classmethod
    async def get_asyncpg_connection(cls, database_url: str) -> asyncpg.Connection:
        # Convert postgresql+asyncpg:// to postgresql:// for raw asyncpg
        url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        return await asyncpg.connect(url)
