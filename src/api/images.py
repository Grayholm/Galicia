from fastapi import APIRouter, File, Depends, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles

from src.api.dependencies import DBDep
from src.exceptions import ObjectNotFoundException, ServiceUnavailableError
from src.services.images import BASE_UPLOAD_DIR, ImageService

router = APIRouter()
router.mount("/static", StaticFiles(directory=str(BASE_UPLOAD_DIR)), name="static")

@router.post("/hotels/{hotel_id}/images")
async def upload_hotel_image(
    db: DBDep,
    hotel_id: int,
    file: UploadFile = File(...),
):
    try:
        return await ImageService(db).upload_hotel_image(hotel_id, file)
    except ObjectNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ServiceUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.delete("/images/{image_id}")
async def delete_image(
    db: DBDep,
    image_id: int,
):
    try:
        return await ImageService(db).delete_image(image_id)
    except ObjectNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ServiceUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
