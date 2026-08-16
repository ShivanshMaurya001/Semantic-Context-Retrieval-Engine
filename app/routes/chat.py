from fastapi import APIRouter

from app.schemas.schemas import QueryRequest
from app.services.vector_service import search_chunks
from app.services.llm_service import generate_answer


router = APIRouter()


@router.post("/query")
def query_documents(request: QueryRequest):

    results = search_chunks(
        question=request.question,
        file_id=request.file_id
    )

    documents = results["documents"][0]

    context = "\n\n".join(
        f"[Chunk {i + 1}]\n{document}"
        for i, document in enumerate(documents)
    )

    answer = generate_answer(
        question=request.question,
        context=context
    )

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