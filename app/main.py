from fastapi import FastAPI, UploadFile, File

app = FastAPI()


@app.post("/upload")
def upload_pdf(file: UploadFile = File(...)):
    return {
        "filename": file.filename
    }