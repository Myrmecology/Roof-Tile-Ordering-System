# ============================================================
# ROOF TILE ORDERING SYSTEM — Database Configuration
# ============================================================

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
import os

load_dotenv()

# ------------------------------------------------------------
# DATABASE URL
# ------------------------------------------------------------
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./data/roof_supplies.db"
)

# ------------------------------------------------------------
# ASYNC ENGINE
# ------------------------------------------------------------
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)

# ------------------------------------------------------------
# SESSION FACTORY
# ------------------------------------------------------------
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# ------------------------------------------------------------
# DECLARATIVE BASE
# ------------------------------------------------------------
class Base(DeclarativeBase):
    pass

# ------------------------------------------------------------
# DEPENDENCY — Used in FastAPI route handlers
# ------------------------------------------------------------
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# ------------------------------------------------------------
# DATABASE INITIALIZATION
# ------------------------------------------------------------
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)