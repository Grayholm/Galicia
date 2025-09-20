import shutil
from pathlib import Path
from fastapi import UploadFile, HTTPException
import uuid

BASE_UPLOAD_DIR = Path(r"E:\proj\src\images")

class FileStorageService:
    def __init__(self, base_upload_dir = BASE_UPLOAD_DIR):
        self.base_upload_dir = base_upload_dir
        self.base_upload_dir.mkdir(exist_ok=True)
        
        self.hotels_dir = self.base_upload_dir / "hotels"
        self.hotels_dir.mkdir(exist_ok=True)
    
    def generate_unique_filename(self, original_filename: str) -> str:
        extension = original_filename.split('.')[-1]
        unique_id = uuid.uuid4().hex
        return f"{unique_id}.{extension}"
    
    def save_file(self, file: UploadFile, hotel_id: int) -> dict:
        try:
            hotel_dir = self.hotels_dir / str(hotel_id)
            hotel_dir.mkdir(exist_ok=True)
            
            filename = self.generate_unique_filename(file.filename)
            file_path = hotel_dir / filename

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            return {
                "file_name": filename,
                "file_path": str(file_path),
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    
    def delete_file(self, file_path: str) -> bool:
        try:
            path = Path(file_path)
            
            if not path.exists():
                print(f"Файл не найден: {file_path}")
                return False
            
            directory = path.parent
            filename = path.stem
            extension = path.suffix
            
            if path.exists():
                path.unlink()
                print(f"Удален оригинальный файл: {path}")
            
            sizes = [1000, 500, 200]
            for size in sizes:
                resized_filename = f"{filename}_{size}px{extension}"
                resized_path = directory / resized_filename
                
                if resized_path.exists():
                    resized_path.unlink()
                    print(f"Удален ресайзнутый файл: {resized_path}")
                else:
                    print(f"Ресайзнутый файл не найден: {resized_path}")
            
            if directory.exists() and not any(directory.iterdir()):
                directory.rmdir()
                print(f"Удалена пустая папка: {directory}")
            
            return True
            
        except Exception as e:
            print(f"Ошибка при удалении файлов: {e}")
            return False
    
    def get_file_url(self, file_path: str) -> str:
        relative_path = Path(file_path).relative_to(self.base_upload_dir)
        return f"/static/{relative_path}"