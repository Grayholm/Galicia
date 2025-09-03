from typing import Annotated
from fastapi import Query, Depends, Request, HTTPException
from pydantic import BaseModel, Field

from services.auth import AuthService


class PaginationParams(BaseModel):
    page: Annotated[int | None, Query(1, ge=1)]
    per_page: Annotated[int | None, Query(2, ge=1, lt=30)]

PaginationDep = Annotated[PaginationParams, Depends()]


def get_token(request: Request) -> str:
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Вы не предоставили куки-токен")
    
    return access_token
        

def get_current_user_id(token = Depends(get_token)) -> int:
    data = AuthService().decode_token(token)
    return data["user_id"]

UserIdDep = Annotated[int, Depends(get_current_user_id)]


class ItemFilter(BaseModel):
    hotel_id: int | None = Field(None, description="Айди отеля")
    title: str | None = Field(None, description="Фильтр по имени")
    price_min: float | None = Field(None, description="Минимальная цена")
    price_max: float | None = Field(None, description="Максимальная цена")

RoomsFilterDep = Annotated[ItemFilter, Depends()]