"""FastAPI backend for Auto-Form Filler — JS Windshields."""
import os
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent / ".env")

from extractor import extract_fields
from form_filler import fill_form
from config import ACCIDENT_DESCRIPTIONS, OCCUPANTS

app = FastAPI(title="Auto-Form Filler — JS Windshields")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent.parent

# Serve frontend, claim forms, and logo as static assets
FRONTEND_DIR  = BASE_DIR / "frontend"
CLAIM_FORMS_DIR = BASE_DIR / "claim_forms"
LOGO_DIR      = BASE_DIR / "logo"

app.mount("/static",       StaticFiles(directory=str(FRONTEND_DIR)),    name="static")
app.mount("/claim_forms",  StaticFiles(directory=str(CLAIM_FORMS_DIR)), name="claim_forms")
app.mount("/logo",         StaticFiles(directory=str(LOGO_DIR)),        name="logo")


@app.get("/")
def root():
    return FileResponse(str(FRONTEND_DIR / "claim_filler_v2.html"))


@app.post("/extract")
async def extract(govt_id_pdf: UploadFile = File(...)):
    """Proxy Claude extraction — avoids browser CORS restrictions."""
    if not os.getenv("API_KEY"):
        raise HTTPException(500, "API_KEY not set in environment")
    if not govt_id_pdf.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Please upload a PDF file.")
    pdf_bytes = await govt_id_pdf.read()
    try:
        return extract_fields(pdf_bytes)
    except Exception as e:
        raise HTTPException(500, f"Extraction failed: {str(e)}")


@app.post("/process")
async def process(
    govt_id_pdf: UploadFile = File(...),
    cashless: str = Form(...),           # "cashless" or "non-cashless"
    insurer_file: str = Form(...),       # filename from claim_forms/ e.g. "United-India-Claim-Form.pdf"
    accident_date: str = Form(...),      # DD/MM/YYYY
    accident_time: str = Form(...),      # HH:MM
    am_pm: str = Form(...),             # "AM" or "PM"
    accident_place: str = Form(...),
    accident_type: str = Form(...),      # "stone_hit" | "branch_moving" | "branch_parked"
    estimate_amount: str = Form(""),     # optional
):
    if not os.getenv("API_KEY"):
        raise HTTPException(500, "API_KEY not set in environment")

    if not govt_id_pdf.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Please upload a PDF file.")

    # 1. Read uploaded file
    pdf_bytes = await govt_id_pdf.read()

    # 2. Extract fields from govt ID PDF via Claude
    try:
        extracted = extract_fields(pdf_bytes)
    except Exception as e:
        raise HTTPException(500, f"Extraction failed: {str(e)}")

    # 3. Build the complete data dict
    data = {
        **extracted,
        "cashless": cashless == "cashless",
        "accident_date": accident_date,
        "accident_time": accident_time,
        "am_pm": am_pm.upper(),
        "accident_place": accident_place,
        "accident_description": ACCIDENT_DESCRIPTIONS.get(accident_type, ""),
        "occupants": OCCUPANTS.get(accident_type, "1"),
        "estimate_amount": estimate_amount.strip() if estimate_amount else "",
    }

    # 4. Fill the form PDF
    try:
        filled_pdf = fill_form(data, insurer_file)
    except Exception as e:
        raise HTTPException(500, f"Form filling failed: {str(e)}")

    # 5. Return the filled PDF
    return Response(
        content=filled_pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=filled_claim_form.pdf"
        },
    )


@app.get("/health")
def health():
    return {"status": "ok"}
