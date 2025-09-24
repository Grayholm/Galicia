from fastapi import APIRouter, HTTPException, Response

from api.dependencies import DBDep
from src.services.auth import AuthService
from src.schemas.users import UserRequestAddRegister, UserAdd, UserLogin
from utils.auth_utils import UserIdDep


router = APIRouter(prefix='/auth', tags=["Аутентификация и авторизация"])



@router.post("/register")
async def register_user(data: UserRequestAddRegister, db: DBDep):
    hashed_password = AuthService().hash_password(data.password)
    new_user_data = UserAdd(
        first_name = data.first_name,
        last_name = data.last_name,
        nickname = data.nickname,
        birth_day = data.birth_day,
        email = data.email,
        hashed_password = hashed_password
        )
    await db.users.add(new_user_data)
    await db.commit()

    return {"status": "Ok", "data": "Вы успешно зарегистрировались!"}



@router.post("/login")
async def login_user(
    data: UserLogin,
    response: Response,
    db: DBDep
    ):
    user = await db.users.get_user_with_hashed_password(user_email=data.email)
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь с таким email не зарегистрирован")
    if not AuthService().verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Введен неверный пароль")
    access_token = AuthService().create_access_token({"user_id": user.id})
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