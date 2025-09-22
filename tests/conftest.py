import pytest

from src.config import settings
from src.db import Base, engine_null_pool
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.models import *


@pytest.fixture(scope='session', autouse=True)
def check_test_mode():
    assert settings.MODE == "TEST"

@pytest.fixture(scope='session', autouse=True)
async def setup_database(check_test_mode):

    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

@pytest.fixture(scope='session', autouse=True)
async def register_user(setup_database):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        await ac.post(
            "/auth/register",
            json={
                "first_name": "Alex",
                "last_name": "Smith",
                "nickname": "Gordon",
                "birth_day": "1990-01-01",
                "email": "alexsmith1990@gmail.com",
                "password": "smith0101",
            }
        )

    print('PRIVETTTT')