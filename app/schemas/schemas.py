from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str
    file_id: str | None = None