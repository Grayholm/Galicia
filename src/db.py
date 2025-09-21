from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from src.config import settings
from sqlalchemy.orm import DeclarativeBase

engine = create_async_engine(settings.db_url, echo=True)
engine_null_pool = create_async_engine(settings.db_url, poolclass=NullPool)

async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)
async_session_maker_null_pool = async_sessionmaker(bind=engine_null_pool, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

