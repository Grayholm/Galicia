from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from src.config import settings
from sqlalchemy.orm import DeclarativeBase

db_params = {}
if settings.MODE == 'TEST':
    db_params = {'poolclass': NullPool}

engine = create_async_engine(settings.db_url, echo=True, **db_params)
# engine_null_pool = create_async_engine(settings.db_url, poolclass=NullPool)

async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

