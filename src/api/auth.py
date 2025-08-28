from fastapi import APIRouter
from passlib.context import CryptContext

from src.schemas.users import UserRequestAdd, UserAdd
from src.repositories.users import UsersRepository
from src.db import async_session_maker


router = APIRouter(prefix='/auth', tags=["Аутентификация и авторизация"])

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

@router.post("/register")
async def register_user(data: UserRequestAdd):
    hashed_password = pwd_context.hash(data.password)
    new_user_data = UserAdd(
        first_name = data.first_name,
        last_name = data.last_name,
        nickname = data.nickname,
        birth_day = data.birth_day,
        email = data.email,
        phone_number = data.phone_number,
        hashed_password = hashed_password
        )
    async with async_session_maker() as session:
        await UsersRepository(session).add(new_user_data)
        await session.commit()

    return {"status": "Ok", "data": "Вы успешно зарегистрировались!"}