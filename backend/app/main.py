import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from .models import PreviewResponse, SIFRequest
from .sif import build_sif_rows, build_xlsx_bytes, load_banks

BASE_DIR = Path(__file__).resolve().parents[1]
BANKS_PATH = BASE_DIR / "data" / "omani_banks.json"
DEFAULT_DEV_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
]


def build_cors_origins() -> list[str]:
    origins_raw = os.getenv("CORS_ALLOW_ORIGINS", "")
    configured = [origin.strip() for origin in origins_raw.split(",") if origin.strip()]
    if configured:
        return configured
    return DEFAULT_DEV_ORIGINS


app = FastAPI(title="Oman WPS SIF API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=build_cors_origins(),
    allow_origin_regex=os.getenv("CORS_ALLOW_ORIGIN_REGEX", r"https://.*\\.vercel\\.app"),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition", "X-Generated-Filename"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/banks")
def get_banks() -> dict:
    if not BANKS_PATH.exists():
        raise HTTPException(status_code=500, detail="Bank dataset missing.")
    return {"banks": load_banks(BANKS_PATH)}


@app.post("/api/sif/preview", response_model=PreviewResponse)
def preview_sif(payload: SIFRequest) -> PreviewResponse:
    if not payload.employer_cr.strip() or not payload.payer_cr.strip() or not payload.payer_account.strip():
        raise HTTPException(
            status_code=422,
            detail="Employer CR-NO, Payer CR-NO, and Payer Account Number are required.",
        )

    rows, normalized, filename, total_salaries, number_of_records = build_sif_rows(payload)

    return PreviewResponse(
        filename=filename,
        total_salaries=total_salaries,
        number_of_records=number_of_records,
        sheet_name=payload.sheet_name.strip() or "Sheet1",
        row_count=len(rows),
        normalized_employees=normalized,
    )


@app.post("/api/sif/generate")
def generate_sif(payload: SIFRequest) -> Response:
    if not payload.employer_cr.strip() or not payload.payer_cr.strip() or not payload.payer_account.strip():
        raise HTTPException(
            status_code=422,
            detail="Employer CR-NO, Payer CR-NO, and Payer Account Number are required.",
        )

    rows, _, filename, _, _ = build_sif_rows(payload)
    sheet_name = payload.sheet_name.strip() or "Sheet1"
    workbook_bytes = build_xlsx_bytes(rows, sheet_name)

    return Response(
        content=workbook_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Generated-Filename": filename,
        },
    )
