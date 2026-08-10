from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import uuid


router = APIRouter()


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
def upload_pdf(file: UploadFile = File(...)):

    # Check file extension
    file_extension = Path(file.filename).suffix.lower()

    if file_extension != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    # Generate unique ID of pdf file jo upload hua ha 
    file_id = uuid.uuid4()

    # Create unique filename of file 
    unique_filename = f"{file_id}.pdf"

    # Create file path and yahan pe file ko save karenge uploads folder me or
    #  upload route me file ko save karenge uploads folder me
    file_path = UPLOAD_DIR / unique_filename

    # Save PDF to the uploads directory so ham use access kar paye or usko read kar sake 
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    return {  # normal response ha file hone ke baad uske barre me
        "file_id": str(file_id),
        "original_filename": file.filename,
        "saved_filename": unique_filename,
        "file_path": str(file_path)
    }