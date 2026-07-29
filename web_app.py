import logging
import os
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from pdf_parser.extractor import RevolutExtractor
from analyzer.categorizer import Categorizer
from analyzer.statistics import Statistics
from exporter.excel_generator import ExcelGenerator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Bank Statement Analyzer")

UPLOAD_DIR = Path("/tmp/bank_uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")


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

    categorizer = Categorizer()
    categorizer.categorize_batch(transactions)
    stats = Statistics().compute(transactions)

    xlsx_filename = f"Bank_analysis_{datetime.now().strftime('%Y-%m-%d')}_{session_id}.xlsx"
    xlsx_path = UPLOAD_DIR / xlsx_filename

    gen = ExcelGenerator(transactions, stats, source_pdf=file.filename)
    gen.generate(str(xlsx_path))

    return {
        "status": "success",
        "transactions": stats.total_count,
        "income": round(stats.total_income, 2),
        "expenses": round(stats.total_expenses, 2),
        "balance": round(stats.balance, 2),
        "unknown": stats.unknown_count,
        "categories": len(stats.category_stats),
        "download_url": f"/download/{xlsx_filename}",
    }


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
