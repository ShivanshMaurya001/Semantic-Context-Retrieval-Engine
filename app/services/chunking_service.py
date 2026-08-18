def create_chunks(text, chunk_size=1000, overlap=100):

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end]

        chunks.append(chunk)

        start = end - overlap

    return chunks


def create_page_chunks(pages, file_id, chunk_size=500, overlap=100):

    all_chunks = []

    chunk_counter = 0

    for page in pages:

        page_number = page["page_number"]
        text = page["text"]

        chunks = create_chunks(
            text,
            chunk_size,
            overlap
        )

        for i in range(len(chunks)):

            chunk_data = {
                "chunk_id": f"{file_id}_{chunk_counter}",
                "file_id": file_id,
                "page_number": page_number,
                "chunk_text": chunks[i]
            }

            all_chunks.append(chunk_data)

            chunk_counter += 1

    return all_chunks