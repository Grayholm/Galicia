from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles

from src.api.dependencies import DBDep
from src.exceptions import ObjectNotFoundException, ServiceUnavailableError, ImageServiceException
from src.services.images import BASE_UPLOAD_DIR, ImageService

router = APIRouter(prefix="/hotels", tags=["Изображения"])
router.mount("/static", StaticFiles(directory=str(BASE_UPLOAD_DIR)), name="static")


@router.post(
    "/{hotel_id}/images",
    summary='Добавить изображение к отелю',
)
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
    except ImageServiceException as e:
        raise HTTPException(status_code=415, detail=f"Недопустимый тип файла. Допустимы изображения формата: jpeg, png, webp")


@router.delete(
    "/images/{image_id}",
    summary='Удалить изображение',
    description='Удаление изображения по его ID',
)
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
