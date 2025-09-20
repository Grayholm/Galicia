from pathlib import Path
from time import sleep
from src.tasks.celery_app import celery_instance
from PIL import Image
import os

@celery_instance.task(name="test_task")
def test_task():
    sleep(5)
    print("Test task completed")


@celery_instance.task(name="resize_image")
def resize_image(image_path: str, hotel_or_room: str, hotel_id: int):
    sizes = [1000, 500, 200]
    output_folder = f'src/images/{hotel_or_room}/{hotel_id}'

    img = Image.open(image_path)

    base_name = os.path.basename(image_path)
    name, ext = os.path.splitext(base_name)

    for size in sizes:

        img_resized = img.resize((size, int(img.height * (size / img.width))), Image.Resampling.LANCZOS)

        new_file_name = f"{name}_{size}px{ext}"

        output_path = os.path.join(output_folder, new_file_name)

        img_resized.save(output_path)
    print(f"Изображение сохранено в следующих размерах: {sizes} в папке {output_folder}")