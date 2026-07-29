import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

from pdf_parser.extractor import RevolutExtractor
from analyzer.categorizer import Categorizer
from analyzer.statistics import Statistics
from exporter.excel_generator import ExcelGenerator
from exporter.google_sheets import GoogleSheetsExporter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Bank Statement Analyzer")

UPLOAD_DIR = Path("/tmp/bank_uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

_SESSIONS: dict[str, dict] = {}


def _categorize(transactions):
    cat = Categorizer()
    cat.categorize_batch(transactions)
    return Statistics().compute(transactions)


def _filter_transactions(transactions, filter_type: str):
    if filter_type == "income":
        return [t for t in transactions if t.amount > 0]
    if filter_type == "expense":
        return [t for t in transactions if t.amount < 0]
    return transactions


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    with open("templates/index.html") as f:
        return f.read()


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)) -> dict:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    session_id = uuid.uuid4().hex[:12]
    pdf_path = UPLOAD_DIR / f"{session_id}_{file.filename}"

    content = await file.read()
    pdf_path.write_bytes(content)

    try:
        extractor = RevolutExtractor()
        transactions = extractor.extract(str(pdf_path))
    except Exception as e:
        logger.exception("PDF parsing failed")
        pdf_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail=f"PDF parsing error: {e}")

    if not transactions:
        pdf_path.unlink(missing_ok=True)
        return {"status": "error", "detail": "No transactions found in the PDF"}

    stats = _categorize(transactions)

    _SESSIONS[session_id] = {
        "filename": file.filename,
        "transactions": transactions,
        "stats": stats,
    }

    xlsx_filename = f"Bank_analysis_{datetime.now().strftime('%Y-%m-%d')}_{session_id}.xlsx"
    xlsx_path = UPLOAD_DIR / xlsx_filename
    gen = ExcelGenerator(transactions, stats, source_pdf=file.filename)
    gen.generate(str(xlsx_path))

    return {
        "status": "success",
        "session_id": session_id,
        "transactions": stats.total_count,
        "income": round(stats.total_income, 2),
        "expenses": round(stats.total_expenses, 2),
        "balance": round(stats.balance, 2),
        "unknown": stats.unknown_count,
        "categories": len(stats.category_stats),
        "download_url": f"/download/{xlsx_filename}",
    }


class ExportRequest(BaseModel):
    session_id: str
    filter: str = "all"
    format: str = "xlsx"


@app.post("/export")
async def export(req: ExportRequest) -> JSONResponse:
    session = _SESSIONS.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired")

    txs = _filter_transactions(session["transactions"], req.filter)
    if not txs:
        raise HTTPException(status_code=400, detail="No transactions match the filter")

    stats = _categorize(txs)

    if req.format == "google_sheets":
        try:
            url = GoogleSheetsExporter().export(txs, stats, session["filename"])
            return JSONResponse({"status": "success", "sheet_url": url})
        except Exception as e:
            logger.exception("Google Sheets export failed")
            raise HTTPException(status_code=500, detail=f"Google Sheets error: {e}")

    xlsx_filename = f"Bank_analysis_{req.filter}_{datetime.now().strftime('%Y-%m-%d')}_{req.session_id[:8]}.xlsx"
    xlsx_path = UPLOAD_DIR / xlsx_filename
    gen = ExcelGenerator(txs, stats, source_pdf=session["filename"])
    gen.generate(str(xlsx_path))

    return JSONResponse({
        "status": "success",
        "transactions": stats.total_count,
        "income": round(stats.total_income, 2),
        "expenses": round(stats.total_expenses, 2),
        "balance": round(stats.balance, 2),
        "download_url": f"/download/{xlsx_filename}",
    })


@app.get("/download/{filename}")
async def download(filename: str) -> FileResponse:
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        str(file_path),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filename,
    )


if __name__ == "__main__":
    uvicorn.run("web_app:app", host="0.0.0.0", port=8000, reload=True)
