from fastapi import APIRouter

from fastapi_cache.decorator import cache

from src.api.dependencies import DBDep
from src.schemas.facilities import FacilityAdd

router = APIRouter(prefix="/facilities", tags=["Удобства"])

@router.post('')
async def add_facility(facility: FacilityAdd, db: DBDep):
    added_facility = await db.facilities.add(facility)
    await db.commit()

    return {"status": "Ok", "data": added_facility}


@router.get('')
@cache(expire=10)
async def get_facilities(db: DBDep):
    print("ИДУ В БАЗУ ДАННЫХ")
    return await db.facilities.get_all()