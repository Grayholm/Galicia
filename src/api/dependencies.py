from datetime import date
from typing import Annotated
from fastapi import Query, Depends
from pydantic import BaseModel, Field

from utils.db_manager import DBManager
from src.db import async_session_maker


class PaginationParams(BaseModel):
    page: Annotated[int | None, Query(1, ge=1)]
    per_page: Annotated[int | None, Query(2, ge=1, lt=30)]

PaginationDep = Annotated[PaginationParams, Depends()]


class ItemFilter(BaseModel):
    # hotel_id: int = Field(..., description="Айди отеля")
    title: str | None = Field(None, description="Фильтр по имени")
    price_min: float | None = Field(None, description="Минимальная цена")
    price_max: float | None = Field(None, description="Максимальная цена")
    date_from: date | None = Field(None)
    date_to: date | None = Field(None)

RoomsFilterDep = Annotated[ItemFilter, Depends()]

async def get_db():
    async with DBManager(session_factory=async_session_maker()) as db:
        yield db

DBDep = Annotated[DBManager, Depends(get_db)]