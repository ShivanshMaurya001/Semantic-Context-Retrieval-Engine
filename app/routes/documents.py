from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import uuid

from app.database.database import SessionLocal
from app.database.models import Document
from app.services.pdf_service import extract_text_from_pdf
from app.services.chunking_service import create_page_chunks
from app.services.vector_service import store_chunks


router = APIRouter()


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


MAX_FILE_SIZE = 10 * 1024 * 1024


@router.post("/upload")
def upload_pdf(file: UploadFile = File(...)):

    file_extension = Path(file.filename).suffix.lower()

    if file_extension != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    file_content = file.file.read()

    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File size must be less than or equal to 10 MB"
        )

    file_id = uuid.uuid4()

    unique_filename = f"{file_id}.pdf"

    file_path = UPLOAD_DIR / unique_filename

    with open(file_path, "wb") as buffer:
        buffer.write(file_content)

    db = SessionLocal()

    try:

        document = Document(
            file_id=str(file_id),
            filename=file.filename,
            page_count=0,
            status="processing"
        )

        db.add(document)
        db.commit()

        try:
            pages = extract_text_from_pdf(file_path)

        except ValueError as e:

            document.status = "failed"
            db.commit()

            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

        document.page_count = len(pages)

        chunks = create_page_chunks(
            pages,
            str(file_id)
        )

        print("Total chunks created:", len(chunks))

        store_chunks(chunks)

        document.status = "ready"

        db.commit()

        return {
            "file_id": str(file_id),
            "filename": file.filename,
            "status": "ready"
        }

    except HTTPException:
        raise

    except Exception:
        document.status = "failed"
        db.commit()

        raise HTTPException(
            status_code=500,
            detail="Document processing failed"
        )

    finally:

        db.close()


@router.get("/documents")
def get_documents():

    db = SessionLocal()

    try:
        documents = db.query(Document).all()

        return [
            {
                "file_id": document.file_id,
                "filename": document.filename,
                "page_count": document.page_count,
                "status": document.status
            }
            for document in documents
        ]

    finally:
        db.close()