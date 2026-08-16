from fastapi import APIRouter, HTTPException

from app.schemas.schemas import QueryRequest
from app.database.database import SessionLocal
from app.database.models import Document
from app.services.vector_service import search_chunks
from app.services.llm_service import generate_answer


router = APIRouter()


@router.post("/query")
def query_documents(request: QueryRequest):

    # Check if the question is empty
    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    # Check if the requested document exists
    if request.file_id:

        db = SessionLocal()

        try:
            document = db.query(Document).filter(
                Document.file_id == request.file_id
            ).first()

            if not document:
                raise HTTPException(
                    status_code=404,
                    detail="Document not found"
                )

        finally:
            db.close()

    # Retrieve relevant chunks from ChromaDB
    results = search_chunks(
        question=request.question,
        file_id=request.file_id
    )

    # Get retrieved documents
    documents = results["documents"][0]

    # Combine chunks into one context for the LLM
    context = "\n\n".join(
        f"[Chunk {i + 1}]\n{document}"
        for i, document in enumerate(documents)
    )

    # Generate grounded answer using Gemini
    answer = generate_answer(
        question=request.question,
        context=context
    )

    # Get source metadata
    metadatas = results["metadatas"][0]
    ids = results["ids"][0]

    sources = []

    for i in range(len(metadatas)):
        sources.append(
            {
                "chunk_id": ids[i],
                "file_id": metadatas[i]["file_id"],
                "page_number": metadatas[i]["page_number"]
            }
        )

    return {
        "answer": answer,
        "sources": sources
    }