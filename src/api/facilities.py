from fastapi import APIRouter, HTTPException

from api.dependencies import DBDep
from schemas.facilities import FacilityAdd
from utils.auth_utils import UserIdDep

router = APIRouter(prefix="/facilities", tags=["Удобства"])

@router.post('')
async def add_facility(fasility: FacilityAdd, db: DBDep):
    added_fasility = await db.facilities.add(fasility)
    await db.commit()

    return {"status": "Ok", "data": added_fasility}


@router.get('')
async def get_facilities(db: DBDep):
    facilities = await db.facilities.get_all()

    return facilities