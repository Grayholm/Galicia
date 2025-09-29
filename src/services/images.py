import logging
import shutil
from pathlib import Path
from fastapi import UploadFile
import uuid

from src.exceptions import ObjectNotFoundException, ServiceUnavailableError
from src.schemas.images import ImageAdd
from src.services.base import BaseService
from src.tasks.tasks import resize_image

BASE_UPLOAD_DIR = Path(r"E:\proj\src\images")


class ImageService(BaseService):
    def __init__(self, db, base_upload_dir: Path = BASE_UPLOAD_DIR):
        super().__init__(db)
        self.base_upload_dir = base_upload_dir
        self.base_upload_dir.mkdir(parents=True, exist_ok=True)
        self.hotels_dir = self.base_upload_dir / "hotels"
        self.hotels_dir.mkdir(exist_ok=True)

        logging.info(f"ImageService initialized with base directory: {base_upload_dir}")

    def _generate_unique_filename(self, original_filename: str) -> str:
        """Генерация уникального имени файла"""
        extension = original_filename.split(".")[-1]
        unique_id = uuid.uuid4().hex
        filename = f"{unique_id}.{extension}"

        logging.debug(f"Generated unique filename: {filename} for original: {original_filename}")
        return filename

    def _save_file_to_disk(self, file: UploadFile, hotel_id: int) -> dict:
        """Сохранение файла на диск"""
        logging.info(f"Saving file to disk for hotel {hotel_id}: {file.filename}")

        try:
            hotel_dir = self.hotels_dir / str(hotel_id)
            hotel_dir.mkdir(parents=True, exist_ok=True)
            logging.debug(f"Using hotel directory: {hotel_dir}")

            filename = self._generate_unique_filename(file.filename)
            file_path = hotel_dir / filename

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            logging.info(f"File saved successfully: {file_path}")

            return {
                "file_name": filename,
                "file_path": str(file_path),
            }

        except Exception as e:
            logging.error(f"Failed to save file for hotel {hotel_id}: {e}")
            raise

    def _delete_file_from_disk(self, file_path: str) -> bool:
        """Удаление файла с диска"""
        logging.info(f"Deleting file from disk: {file_path}")

        try:
            path = Path(file_path)

            if not path.exists():
                logging.warning(f"File not found for deletion: {file_path}")
                return False

            directory = path.parent
            filename = path.stem
            extension = path.suffix

            # Удаляем оригинальный файл
            if path.exists():
                path.unlink()
                logging.info(f"Original file deleted: {path}")

            # Удаляем ресайзнутые версии
            sizes = [1000, 500, 200]
            deleted_resized_count = 0

            for size in sizes:
                resized_filename = f"{filename}_{size}px{extension}"
                resized_path = directory / resized_filename

                if resized_path.exists():
                    resized_path.unlink()
                    deleted_resized_count += 1
                    logging.debug(f"Resized file deleted: {resized_path}")

            logging.info(f"Deleted {deleted_resized_count} resized versions")

            # Удаляем пустую папку
            if directory.exists() and not any(directory.iterdir()):
                directory.rmdir()
                logging.info(f"Empty directory deleted: {directory}")

            logging.info(f"File deletion completed successfully: {file_path}")
            return True

        except Exception as e:
            logging.error(f"Failed to delete file {file_path}: {e}")
            return False

    def _get_file_url(self, file_path: str) -> str:
        """Генерация URL для файла"""
        try:
            relative_path = Path(file_path).relative_to(self.base_upload_dir)
            url = f"/static/{relative_path}"

            logging.debug(f"Generated file URL: {url} for path: {file_path}")
            return url

        except Exception as e:
            logging.error(f"Failed to generate URL for file {file_path}: {e}")
            raise

    async def upload_hotel_image(self, hotel_id: int, file: UploadFile) -> dict:
        """Полная бизнес-логика загрузки изображения отеля"""
        logging.info(f"Starting image upload for hotel {hotel_id}: {file.filename}")

        # Проверяем существование отеля
        try:
            hotel = await self.db.hotels.get_one(id=hotel_id)
        except ObjectNotFoundException:
            raise ObjectNotFoundException(f"Hotel with id {hotel_id} not found")

        # try:
        # Сохраняем файл на диск
        file_info = self._save_file_to_disk(file, hotel_id)

        # Создаем запись в БД
        image = ImageAdd(
            title=file.filename,
            url=file_info["file_path"],
        )

        image_entity = await self.db.images.add(image)

        # Создаем связь отель-изображение
        association_data = {"hotel_id": hotel_id, "image_id": image_entity.id}
        await self.db.hotels_images.add_image(association_data)
        await self.db.commit()

        resize_image.delay(
            image_path=file_info["file_path"],
            hotel_or_room="hotels",
            hotel_id=hotel_id
        )

        logging.info(f"Image uploaded successfully for hotel {hotel_id}, image_id: {image_entity.id}")

        return {
            "message": "File uploaded successfully",
            "url": self._get_file_url(file_info["file_path"]),
            "image_id": image_entity.id
        }


    async def delete_image(self, image_id: int) -> dict:
        """Полная бизнес-логика удаления изображения"""
        logging.info(f"Starting image deletion: {image_id}")

        # Получаем изображение
        image = await self.db.images.get_one_or_none(id=image_id)
        if not image:
            logging.warning(f"Image not found for deletion: {image_id}")
            raise ObjectNotFoundException(f"Image with id {image_id} not found")

        try:
            # Удаляем файл с диска
            delete_success = self._delete_file_from_disk(image.url)
            if not delete_success:
                logging.warning(f"File deletion failed for image {image_id}, but continuing with DB cleanup")

            # Удаляем связи и запись из БД
            await self.db.hotels_images.delete(image_id=image_id)
            await self.db.images.delete(id=image_id)
            await self.db.commit()

            logging.info(f"Image deleted successfully: {image_id}")

            return {"message": "Image deleted successfully"}

        except ObjectNotFoundException:
            raise
        except Exception as e:
            logging.error(f"Image deletion failed for image {image_id}: {e}")
            raise ServiceUnavailableError("Image upload failed due to technical issues")


