from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from transformers import pipeline
import fitz  # PyMuPDF

app = FastAPI(title="AI Automation FastAPI", version="1.0")

# Allow frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# HuggingFace summarizer
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

@app.get("/")
def home():
    return {"message": "Welcome to AI-Automation-FastAPI 🚀"}

@app.post("/summarize-text/")
async def summarize_text_api(payload: dict):
    text = payload.get("text", "")
    if not text.strip():
        raise HTTPException(status_code=400, detail="No text provided")
    summary = await run_in_threadpool(lambda: summarizer(text, max_length=130, min_length=30, do_sample=False))
    return {"summary": summary[0]['summary_text']}

def extract_text_from_pdf_file(uploaded_file: UploadFile) -> str:
    try:
        pdf_bytes = uploaded_file.file.read()
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in pdf_document:
            text += page.get_text()
        pdf_document.close()
        if not text.strip():
            raise ValueError("No readable text found in PDF.")
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF read error: {e}")

@app.post("/summarize-pdf/")
async def summarize_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a valid PDF file.")
    text = extract_text_from_pdf_file(file)
    text = text[:3000]  # limit for HuggingFace
    if len(text.split()) < 20:
        return {"summary": text}
    summary = await run_in_threadpool(lambda: summarizer(text, max_length=130, min_length=30, do_sample=False))
    return {"summary": summary[0]['summary_text']}
