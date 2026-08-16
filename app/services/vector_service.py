import chromadb

from app.services.embedding_service import generate_embedding


client = chromadb.PersistentClient(
    path="./chroma_db"
)


collection = client.get_or_create_collection(
    name="document_chunks"
)


def store_chunk(chunk):

    embedding = generate_embedding(
        chunk["chunk_text"]
    )

    collection.add(
        ids=[chunk["chunk_id"]],
        documents=[chunk["chunk_text"]],
        embeddings=[embedding],
        metadatas=[
            {
                "file_id": chunk["file_id"],
                "page_number": chunk["page_number"]
            }
        ]
    )

   

def store_chunks(chunks):

    for chunk in chunks:
        store_chunk(chunk)


def search_chunks(question, top_k=3, file_id=None):

    question_embedding = generate_embedding(question)

    if file_id:

        results = collection.query(
            query_embeddings=[question_embedding],
            n_results=top_k,
            where={"file_id": file_id}
        )

    else:

        results = collection.query(
            query_embeddings=[question_embedding],
            n_results=top_k
        )

    return results