# Personal Document Search API

A FastAPI backend that lets users upload PDF documents, extract their text, create chunks and embeddings, search relevant chunks with ChromaDB, and generate grounded answers using Gemini.

## Features

- PDF upload (max 10 MB)
- PDF text extraction
- Page-based chunking
- Gemini embeddings
- ChromaDB vector storage and similarity search
- Document-specific or all-document querying
- Gemini-based grounded answers
- Source references with file ID and page number
- Document listing
- Error handling for invalid PDFs, empty questions, and missing documents

## Tech Stack

- Python
- FastAPI
- Pydantic / Pydantic Settings
- SQLAlchemy + SQLite
- pdfplumber
- Google Gemini API
- ChromaDB

## Project Structure

```text
PERSONAL-DOCUMENT-SEARCH/
├── app/
│   ├── database/
│   ├── routes/
│   ├── schemas/
│   ├── services/
│   ├── utils/
│   └── main.py
├── uploads/
├── chroma_db/
├── .env
├── requirements.txt
└── README.md
```

## Setup

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env` in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=your_database_url
```

Do not commit `.env` or API keys to GitHub.

## Run

```bash
uvicorn app.main:app --reload
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

### Upload PDF

```text
POST /upload
```

Uploads and processes a PDF.

Successful response:

```json
{
  "file_id": "document-id",
  "filename": "example.pdf",
  "status": "ready"
}
```

### Query Documents

```text
POST /query
```

Request:

```json
{
  "question": "What is this document about?",
  "file_id": "optional-file-id"
}
```

`file_id` is optional. If provided, retrieval is restricted to that document.

Response contains:

- `answer`
- `sources`
- source `file_id`
- source `page_number`
- source `chunk_id`

### List Documents

```text
GET /documents
```

Returns uploaded documents with:

- `file_id`
- `filename`
- `page_count`
- `status`

## Query Flow

```text
Question
   ↓
Question Embedding
   ↓
ChromaDB Similarity Search
   ↓
Relevant Chunks
   ↓
Context
   ↓
Gemini
   ↓
Answer + Sources
```

The LLM is instructed to answer from the retrieved context. If the answer is not supported by the document context, the API returns:

```text
The answer was not found in the document.
```

## Error Handling

- Non-PDF upload → `400`
- PDF larger than 10 MB → `400`
- PDF with no extractable text → `400` and document status becomes `failed`
- Empty question → `400`
- Unknown `file_id` → `404`
- Unexpected document-processing error → `500` and document status becomes `failed`



## Testing

Tested through FastAPI Swagger UI:

- Successful PDF upload
- PDF extraction failure
- Chunk creation
- Embedding generation
- ChromaDB storage
- Similarity retrieval
- File-specific retrieval
- Query without `file_id`
- Gemini answer generation
- Grounded/out-of-context answers
- Empty question handling
- Invalid `file_id`
- Document listing
- Successful upload after error-handling changes
