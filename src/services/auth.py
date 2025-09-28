import logging
from datetime import datetime, timedelta, timezone, date

from fastapi import HTTPException
import jwt
from passlib.context import CryptContext
from sqlalchemy.exc import NoResultFound

from src.config import settings
from src.exceptions import EmailIsAlreadyRegisteredException, NicknameIsEmptyException, \
    ObjectNotFoundException, LoginErrorException
from src.schemas.users import UserRequestAddRegister, UserAdd, UserLogin
from src.services.base import BaseService


class AuthService(BaseService):
    pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

    def create_access_token(self, data: dict) -> str:
        logging.debug("Create access token")
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})
        try:
            encoded_jwt = jwt.encode(
                to_encode,
                settings.JWT_SECRET_KEY.get_secret_value(),
                algorithm=settings.JWT_ALGORITHM
            )
            return encoded_jwt
        except Exception as e:
            logging.error(f"Token creation failed: {e}")
            raise

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def decode_token(self, token: str) -> dict:
        logging.debug('Decode token')
        try:
            result = jwt.decode(
                token,
                settings.JWT_SECRET_KEY.get_secret_value(),
                algorithms=[settings.JWT_ALGORITHM],
            )
            logging.info('Token decoded')
            return result
        except jwt.exceptions.InvalidSignatureError:
            logging.error('Invalid token')
            raise HTTPException(status_code=401, detail="Ошибка: Неверная подпись(токен)")

    async def register_user(self, data: UserRequestAddRegister):
        logging.info(f"Начинаем регистрацию пользователя с почтой: {data.email}")

        if data.birth_day and (date.today() - data.birth_day).days < 18 * 365:
            logging.warning(f'Пользователь младше 18, {data.birth_day}')
            raise HTTPException(status_code=400, detail="Возраст должен быть 18+")

        if not data.nickname.strip():
            logging.warning(f'Пустой ник во время регистрации для почты, {data.email}')
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
            logging.info(f'Пользователь успешно зарегистрировался с почтой={new_user.email}')
            return {'message': 'Вы успешно зарегистрировались!'}
        except ObjectNotFoundException as e:
            logging.warning(f'Пользователь ввел уже существующую почту, {new_user.email}')
            raise EmailIsAlreadyRegisteredException


    async def login_and_get_access_token(self, data: UserLogin):
        logging.info(f'Login and get access token for email: {data.email}')
        try:
            user = await self.db.users.get_user_with_hashed_password(user_email=data.email)
        except NoResultFound:
            logging.warning(f'Неверная почта или пароль для пользователя {data.email}')
            raise LoginErrorException

        if not self.verify_password(data.password, user.hashed_password):
            logging.warning(f'Неверная почта или пароль для пользователя {data.email}')
            raise LoginErrorException

        token = self.create_access_token({"user_id": user.id})

        logging.info(f"Login successful: {data.email}, user_id={user.id}")
        return token

    async def get_one_or_none_user(self, user_id: int):
        return await self.db.users.get_one_or_none(id=user_id)
