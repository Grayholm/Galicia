import pytest

from src.config import settings
from src.db import Base, engine_null_pool, async_session_maker_null_pool
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.models import *

import json

from src.schemas.hotels import HotelAdd
from src.schemas.rooms import RoomAdd
from src.utils.db_manager import DBManager


async def add_hotels_from_json(file_path: str, db):
    """
    Читает JSON файл с отелями и добавляет их в БД
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        hotels_data = json.load(f)

    hotels = [HotelAdd.model_validate(hotel) for hotel in hotels_data]
    await db.hotels.add_bulk(hotels)

    await db.commit()

async def add_rooms_from_json(file_path: str, db):
    """
    Читает JSON файл с комнатами и добавляет их в БД
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        rooms_data = json.load(f)

    rooms = [RoomAdd.model_validate(room) for room in rooms_data]
    await db.rooms.add_bulk(rooms)

    await db.commit()


@pytest.fixture(scope='session', autouse=True)
def check_test_mode():
    assert settings.MODE == "TEST"

@pytest.fixture(scope='session', autouse=True)
async def setup_database(check_test_mode):

    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with DBManager(session_factory=async_session_maker_null_pool()) as db:
        await add_hotels_from_json('tests/mock_hotels.json', db)
        await add_rooms_from_json('tests/mock_rooms.json', db)

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