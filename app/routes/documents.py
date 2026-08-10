from fastapi import APIRouter, UploadFile, File
from pathlib import Path
import uuid


router = APIRouter()


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
def upload_pdf(file: UploadFile = File(...)):
    file_id = uuid.uuid4()

    file_extension = Path(file.filename).suffix

    unique_filename = f"{file_id}{file_extension}"

    file_path = UPLOAD_DIR / unique_filename

    return {
        "file_id": str(file_id),
        "original_filename": file.filename,
        "saved_filename": unique_filename,
        "file_path": str(file_path)
    }