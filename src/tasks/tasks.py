import logging
from pathlib import Path

from src.db import SyncSessionLocal
from src.repositories.bookings import BookingsRepository
from src.tasks.celery_app import celery_instance
from PIL import Image
import os

UPLOAD_DIR = Path("/app/src/images")

@celery_instance.task(name="resize_image")
def resize_image(image_filename: str, hotels_or_rooms: str, hotel_id: int):
    logging.debug(f"Вызывается функция image_path с {image_filename}")
    sizes = [1000, 500, 200]
    output_folder = f"src/images/{hotels_or_rooms}/{hotel_id}"
    os.makedirs(output_folder, exist_ok=True)

    image_path = UPLOAD_DIR / hotels_or_rooms / str(hotel_id) / image_filename

    img = Image.open(image_path)

    base_name = os.path.basename(image_path)
    name, ext = os.path.splitext(base_name)

    for size in sizes:
        img_resized = img.resize(
            (size, int(img.height * (size / img.width))), Image.Resampling.LANCZOS
        )

        new_file_name = f"{name}_{size}px{ext}"

        output_path = os.path.join(output_folder, new_file_name)

        img_resized.save(output_path)
    logging.info(f"Изображение сохранено в следующих размерах: {sizes} в папке {output_folder}")


def get_bookings_with_today_checkin_sync():
    with SyncSessionLocal() as session:
        bookings_repo = BookingsRepository(session)
        bookings = bookings_repo.get_bookings_with_today_checkin()
        return bookings

@celery_instance.task(name="booking_today_checkin")
def send_emails_to_users_with_today_checkin():
    bookings = get_bookings_with_today_checkin_sync()
    # обработка бронирований
    return bookings