from fastapi import APIRouter

from app.schemas.schemas import QueryRequest
from app.services.vector_service import search_chunks


router = APIRouter()


@router.post("/query")
def query_documents(request: QueryRequest):

    results = search_chunks(
        question=request.question,
        file_id=request.file_id
    )

    return results