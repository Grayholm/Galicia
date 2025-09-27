from fastapi import APIRouter, Response

from src.api.dependencies import DBDep
from src.schemas.users import UserRequestAddRegister, UserLogin
from src.services.auth.auth import UserService
from src.utils.auth_utils import UserIdDep


router = APIRouter(prefix='/auth', tags=["Аутентификация и авторизация"])



@router.post("/register")
async def register_user(data: UserRequestAddRegister, db: DBDep):
    user = await UserService(db).register_user(data)
    return user


@router.post("/login")
async def login_user(
    data: UserLogin,
    response: Response,
    db: DBDep
    ):

    access_token = await UserService(db).login_and_get_access_token(data=data)
    response.set_cookie("access_token", access_token)
    return {'access_token': access_token}
    
    
@router.get("/me")
async def get_me(user_id: UserIdDep, db: DBDep):
    user = await db.users.get_one_or_none(id=user_id)
    return user

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"status": "Вы вышли из системы"}