from fastapi import APIRouter, HTTPException

from api.dependencies import DBDep
from schemas.fasilities import Fasilities
from utils.auth_utils import UserIdDep

router = APIRouter(prefix="/fasilities", tags=["Удобства"])

@router.post('')
async def add_fasility(fasility: Fasilities, db: DBDep):
    added_fasility = await db.fasilities.add(fasility)
    await db.commit()

    return {"status": "Ok", "data": added_fasility}


@router.get('')
async def get_fasilities(db: DBDep):
    fasilities = await db.fasilities.get_all()

    return fasilities