from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime
from app.database.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String, unique=True, nullable=False)
    filename = Column(String, nullable=False)

    upload_date = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    page_count = Column(Integer, nullable=True)

    status = Column(String, default="uploaded", nullable=False)