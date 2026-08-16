import chromadb

from app.services.embedding_service import generate_embedding


# Connect to persistent ChromaDB
client = chromadb.PersistentClient(
    path="./chroma_db"
)


# Create or connect to collection
collection = client.get_or_create_collection(
    name="document_chunks"
)


# Store one chunk in ChromaDB
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

    