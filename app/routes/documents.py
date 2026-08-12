from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import uuid

from app.database.database import SessionLocal
from app.database.models import Document
from app.services.pdf_service import extract_text_from_pdf
from app.services.chunking_service import create_page_chunks


router = APIRouter()


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


MAX_FILE_SIZE = 10 * 1024 * 1024


@router.post("/upload")
def upload_pdf(file: UploadFile = File(...)):

    # Check file extension
    file_extension = Path(file.filename).suffix.lower()

    if file_extension != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )


    # Read file
    file_content = file.file.read()


    # Check file size
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File size must be less than or equal to 10 MB"
        )


    # Generate unique file ID
    file_id = uuid.uuid4()


    # Create unique filename
    unique_filename = f"{file_id}.pdf"


    # Create file path
    file_path = UPLOAD_DIR / unique_filename


    # Save PDF
    with open(file_path, "wb") as buffer:
        buffer.write(file_content)


    # Create database session
    db = SessionLocal()


    try:

        # Create Document object
        document = Document(
            file_id=str(file_id),
            filename=file.filename,
            page_count=0,
            status="processing"
        )


        # M2: Extract text from PDF
        pages = extract_text_from_pdf(file_path)


        # Update page count
        document.page_count = len(pages)


        # M3: Create chunks from extracted pages
        chunks = create_page_chunks(
            pages,
            str(file_id)
        )


        print("Total chunks created:", len(chunks))


        # Mark document as ready
        document.status = "ready"


        # Add object to database session
        db.add(document)


        # Save changes to database
        db.commit()


        # Return response
        return {
            "file_id": str(file_id),
            "filename": file.filename,
            "status": "processing"
        }


    finally:

        # Close database session
        db.close()