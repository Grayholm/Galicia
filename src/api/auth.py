from fastapi import APIRouter, Response, HTTPException

from src.api.dependencies import DBDep
from src.exceptions import (
    NicknameIsEmptyException,
    EmailIsAlreadyRegisteredException,
    RegisterErrorException,
    LoginErrorException,
)
from src.schemas.users import UserRequestAddRegister, UserLogin
from src.services.auth import AuthService
from src.utils.auth_utils import UserIdDep


router = APIRouter(prefix="/auth", tags=["Аутентификация и авторизация"])


@router.post("/register")
async def register_user(data: UserRequestAddRegister, db: DBDep):
    try:
        user = await AuthService(db).register_user(data)
    except NicknameIsEmptyException:
        raise HTTPException(status_code=400, detail="Ник не может быть пустым")
    except EmailIsAlreadyRegisteredException:
        raise HTTPException(status_code=409, detail="Email уже используется")
    except RegisterErrorException:
        raise HTTPException(status_code=400, detail="Ошибка регистрации")
    return user


@router.post("/login")
async def login_user(data: UserLogin, response: Response, db: DBDep):
    try:
        access_token = await AuthService(db).login_and_get_access_token(data=data)
    except LoginErrorException:
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    response.set_cookie("access_token", access_token)
    return {"access_token": access_token}


@router.get("/me")
async def get_me(user_id: UserIdDep, db: DBDep):
    user = await AuthService(db).get_one_or_none_user(user_id)
    return user


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"status": "Вы вышли из системы"}
