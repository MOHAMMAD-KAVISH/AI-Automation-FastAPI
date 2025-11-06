from fastapi import FastAPI, UploadFile, File
from utils.extractor import extract_text_from_pdf
from utils.summarizer import generate_summary
import os

app = FastAPI(title="AI Automation FastAPI", version="1.0")

@app.get("/")
def home():
    return {"message": "Welcome to AI-Automation-FastAPI 🚀"}

@app.post("/summarize-text/")
async def summarize_text_api(payload: dict):
    text = payload.get("text", "")
    summary = generate_summary(text)
    return {"summary": summary}

@app.post("/summarize-pdf/")
async def summarize_pdf_api(file: UploadFile = File(...)):
    file_path = f"temp_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    text = extract_text_from_pdf(file_path)
    os.remove(file_path)
    summary = generate_summary(text)
    return {"filename": file.filename, "summary": summary}
