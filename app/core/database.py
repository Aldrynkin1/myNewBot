from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .config import settings

naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

engine = create_async_engine(settings.database_url)

SessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession,
    expire_on_commit=False,
)

metadata = MetaData(naming_convention=naming_convention)
Base = declarative_base(metadata=metadata)

async def get_db():
    async with SessionLocal() as db:
        yield db

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)