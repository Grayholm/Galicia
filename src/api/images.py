from fastapi import APIRouter, File, HTTPException, Depends, UploadFile
from fastapi.staticfiles import StaticFiles

from src.schemas.images import ImageAdd
from src.api.dependencies import DBDep
from src.services.images import BASE_UPLOAD_DIR, FileStorageService
from src.tasks.tasks import resize_image

router = APIRouter()

router.mount("/static", StaticFiles(directory=str(BASE_UPLOAD_DIR)), name="static")


@router.post("/hotels/{hotel_id}/images")
async def upload_hotel_image(
    hotel_id: int,
    db: DBDep,
    file: UploadFile = File(...),
    file_service: FileStorageService = Depends(),
):
    hotel = await db.hotels.get_one_or_none(id=hotel_id)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")

    file_info = file_service.save_file(file, hotel_id)

    image = ImageAdd(
        title=file.filename,
        url=file_info["file_path"],
    )

    image = await db.images.add(image)
    db.hotels.add_image(image, hotel)

    association_data = {"hotel_id": hotel_id, "image_id": image.id}
    await db.hotels_images.add_image(association_data)

    await db.commit()

    resize_image.delay(image_path=file_info["file_path"], hotel_or_room="hotels", hotel_id=hotel_id)

    return {
        "message": "File uploaded successfully",
        "url": file_service.get_file_url(file_info["file_path"]),
    }


@router.delete("/images/{image_id}")
async def delete_image(image_id: int, db: DBDep, file_service: FileStorageService = Depends()):
    image = await db.images.get_one_or_none(id=image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    file_service.delete_file(image.url)
    await db.hotels_images.delete(image_id=image_id)
    await db.images.delete(id=image_id)
    await db.commit()

    return {"message": "Image deleted successfully"}
