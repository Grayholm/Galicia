# ruff: noqa: E402
from unittest import mock


mock.patch("fastapi_cache.decorator.cache", lambda *args, **kwargs: lambda f: f).start()

from src.config import settings
from src.db import Base, engine, async_session_maker
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.models import *  # noqa

import json
import pytest

from src.schemas.hotels import HotelAdd
from src.schemas.rooms import RoomAdd
from src.utils.db_manager import DBManager


async def get_db_null_pool():
    async with DBManager(session_factory=async_session_maker) as db:
        yield db


@pytest.fixture(scope="function")
async def db():
    async with DBManager(session_factory=async_session_maker()) as db:
        yield db


@pytest.fixture(scope="module")
async def db_module():
    async with DBManager(session_factory=async_session_maker()) as _db:
        yield _db


async def add_hotels_from_json(file_path: str, db):
    """
    Читает JSON файл с отелями и добавляет их в БД
    """
    with open(file_path, "r", encoding="utf-8") as f:
        hotels_data = json.load(f)

    hotels = [HotelAdd.model_validate(hotel) for hotel in hotels_data]
    await db.hotels.add_bulk(hotels)

    await db.commit()


async def add_rooms_from_json(file_path: str, db):
    """
    Читает JSON файл с комнатами и добавляет их в БД
    """
    with open(file_path, "r", encoding="utf-8") as f:
        rooms_data = json.load(f)

    rooms = [RoomAdd.model_validate(room) for room in rooms_data]
    await db.rooms.add_bulk(rooms)

    await db.commit()


@pytest.fixture(scope="session", autouse=True)
def check_test_mode():
    assert settings.MODE == "TEST"


@pytest.fixture(scope="session", autouse=True)
async def setup_database(check_test_mode):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with DBManager(session_factory=async_session_maker()) as db_:
        await add_hotels_from_json("tests/mock_hotels.json", db_)
        await add_rooms_from_json("tests/mock_rooms.json", db_)


@pytest.fixture(scope="session")
async def ac():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session", autouse=True)
async def register_user(setup_database, ac):
    await ac.post(
        "/auth/register",
        json={
            "first_name": "Alex",
            "last_name": "Smith",
            "nickname": "Gordon",
            "birth_day": "1990-01-01",
            "email": "alexsmith1990@gmail.com",
            "password": "smith0101",
        },
    )


@pytest.fixture(scope="session", autouse=True)
async def authenticated_ac(register_user, ac):
    response = await ac.post(
        "/auth/login",
        json={
            "email": "alexsmith1990@gmail.com",
            "password": "smith0101",
        },
    )
    assert ac.cookies["access_token"] == response.json()["access_token"]
    yield ac
