from typing import Annotated
from fastapi import Depends, HTTPException, Request

from src.services.auth.auth import AuthService


def get_token(request: Request) -> str:
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Вы не предоставили куки-токен")
    
    return access_token
        

def get_current_user_id(token = Depends(get_token)) -> int:
    data = AuthService().decode_token(token)
    return data["user_id"]

UserIdDep = Annotated[int, Depends(get_current_user_id)]