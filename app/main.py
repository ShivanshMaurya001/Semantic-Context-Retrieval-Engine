from fastapi import FastAPI

from app.database.database import engine, Base
from app.database import models
from app.routes.documents import router


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(router)