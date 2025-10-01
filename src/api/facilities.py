from fastapi import APIRouter

from fastapi_cache.decorator import cache

from src.api.dependencies import DBDep
from src.schemas.facilities import FacilityAdd
from src.services.facilities import FacilityService

router = APIRouter(prefix="/facilities", tags=["Удобства"])


@router.post("")
async def add_facility(facility: FacilityAdd, db: DBDep):
    added_facility = await FacilityService(db).add_facility(facility)
    return {"status": "Ok", "data": added_facility}


@router.get("")
@cache(expire=10)
async def get_facilities(db: DBDep):
    return await FacilityService(db).get_facilities()
