from fastapi import APIRouter

from fastapi_cache.decorator import cache

from api.dependencies import DBDep
from schemas.facilities import FacilityAdd
from tasks.tasks import test_task

router = APIRouter(prefix="/facilities", tags=["Удобства"])

@router.post('')
async def add_facility(fasility: FacilityAdd, db: DBDep):
    added_fasility = await db.facilities.add(fasility)
    await db.commit()

    test_task.delay()

    return {"status": "Ok", "data": added_fasility}


@router.get('')
@cache(expire=10)
async def get_facilities(db: DBDep):
    print("ИДУ В БАЗУ ДАННЫХ")
    return await db.facilities.get_all()