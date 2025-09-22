from src.db import async_session_maker
from src.schemas.hotels import Hoteladd
from src.utils.db_manager import DBManager


async def test_add_hotel():
    hotel_data = Hoteladd(title='Hotel 1', location='Сочи')
    async with DBManager(session_factory=async_session_maker()) as db:
        new_hotel = await db.hotels.add(hotel_data)
        print(f'{new_hotel} is added')