from datetime import datetime, timedelta, timezone, date

from fastapi import HTTPException
import jwt
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError, NoResultFound

from src.config import settings
from src.exceptions import EmailIsAlreadyRegisteredException, RegisterErrorException, NicknameIsEmptyException
from src.schemas.users import UserRequestAddRegister, UserAdd, UserLogin
from src.services.base import BaseService


class AuthService(BaseService):
    pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY.get_secret_value(), algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(
                token,
                settings.JWT_SECRET_KEY.get_secret_value(),
                algorithms=[settings.JWT_ALGORITHM],
            )
        except jwt.exceptions.InvalidSignatureError:
            raise HTTPException(status_code=401, detail="Ошибка: Неверная подпись(токен)")

    async def register_user(self, data: UserRequestAddRegister):
        if data.birth_day:
            if (date.today() - data.birth_day).days < 18 * 365:
                raise HTTPException(status_code=400, detail="Возраст должен быть 18+")

        if not data.nickname.strip():
            raise NicknameIsEmptyException

        new_user = UserAdd(
            first_name=data.first_name,
            last_name=data.last_name,
            nickname=data.nickname,
            birth_day=data.birth_day,
            email=data.email,
            hashed_password=self.hash_password(data.password),
        )

        try:
            await self.db.users.add(new_user)
            await self.db.commit()
        except IntegrityError as e:
            err = str(e.orig)
            if "email" in err:
                raise EmailIsAlreadyRegisteredException
            raise RegisterErrorException

        return new_user

    async def login_and_get_access_token(self, data: UserLogin):
        try:
            user = await self.db.users.get_user_with_hashed_password(user_email=data.email)
        except NoResultFound:
            raise HTTPException(status_code=401, detail="Неверный email или пароль")

        if not self.verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Неверный email или пароль")

        return self.create_access_token({"user_id": user.id})

    async def get_one_or_none_user(self, user_id: int):
        return await self.db.users.get_one_or_none(id=user_id)
