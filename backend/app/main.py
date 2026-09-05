import logging
import os
import re
import time
from urllib.parse import parse_qs, unquote, urlparse
import uuid
from contextvars import ContextVar
from io import BytesIO
from typing import Optional

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from pyzbar import pyzbar
from pydantic import BaseModel, Field
import pytesseract

try:
    from google import genai
    from google.genai import types
except ImportError:  # pragma: no cover
    genai = None
    types = None

trace_context: ContextVar[str] = ContextVar("trace_id", default="--------")

class ContextFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        record.trace_id = trace_context.get()
        record.stage = getattr(record, "stage", "SYSTEM")
        return super().format(record)

handler = logging.StreamHandler()
handler.setFormatter(ContextFormatter("[%(asctime)s] [%(levelname)s] [TRACE_ID: %(trace_id)s] [%(stage)s] - %(message)s"))
logger = logging.getLogger("payguard")
logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())
logger.handlers.clear()
logger.addHandler(handler)
logger.propagate = False

class AnalyzeRequest(BaseModel):
    input_type: str = Field(pattern="^(text|url|camera)$")
    content: str = Field(min_length=1, max_length=20000)
    source: str = Field(default="manual", pattern="^(manual|interceptor)$")

class Threat(BaseModel):
    title: str
    detail: str
    severity: str = Field(pattern="^(safe|suspicious|high)$")

class UpiDetails(BaseModel):
    upi_id: Optional[str] = None
    display_name: Optional[str] = None
    phone_number: Optional[str] = None
    amount: Optional[str] = None
    currency: Optional[str] = None
    note: Optional[str] = None
    merchant_code: Optional[str] = None
    confidence: str = Field(default="low", pattern="^(low|medium|high)$")

class GeminiAssessment(BaseModel):
    score: int = Field(ge=0, le=100)
    severity: str = Field(pattern="^(safe|suspicious|high)$")
    label: str
    summary: str
    action: str
    action_detail: str
    entity: str
    threats: list[Threat]
    upi_details: Optional[UpiDetails] = None
    plain_english: str = ""

class AnalyzeResponse(GeminiAssessment):
    source: str
    timestamp: str
    trace_id: str

app = FastAPI(title="PayGuard AI Analysis API", version="1.0.0")
origins = [item.strip() for item in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",") if item.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins or ["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.middleware("http")
async def trace_requests(request, call_next):
    trace_id = uuid.uuid4().hex[:8].upper()
    token = trace_context.set(trace_id)
    started = time.perf_counter()
    try:
        logger.info("Incoming %s request", request.method, extra={"stage": "INGESTION"})
        response = await call_next(request)
        elapsed = (time.perf_counter() - started) * 1000
        logger.info("Request completed in %.1f ms", elapsed, extra={"stage": "RISK_ENGINE"})
        response.headers["X-Trace-Id"] = trace_id
        return response
    except Exception:
        logger.exception("Unhandled request failure", extra={"stage": "ERROR"})
        raise
    finally:
        trace_context.reset(token)

def prompt_for(input_type: str, content: str) -> str:
    if input_type == "image":
        return f"""You are PayGuard AI, a careful UPI scam detection analyst for India. Analyze the supplied image and extracted evidence. Reason specifically about QR-encoded UPI links, including the payee VPA and amount for scam patterns; OCR text such as KYC, refund, OTP, urgency, impersonation of banks/NPCI/government, or payment requests; and visual branding cues in the image itself, including fake bank logos, cloned layouts, badges, and misleading domains. Be conservative: never claim certainty, but clearly identify risk and an actionable next step. Return only JSON matching the supplied schema. Include `plain_english` as a more detailed, calm explanation of what the user should understand and do. If a UPI ID, UPI URI, phone number, payee name, amount, note, or merchant code is visible, populate `upi_details` only with evidence from the input; use null for unknown fields. Never invent an identity. Keep the explanation plain English and actionable.

Extracted evidence:
{content}"""
    return f"""You are PayGuard AI, a careful UPI scam detection analyst for India. Analyze the following {input_type} input. Be conservative: never claim certainty, but clearly identify urgency, impersonation, requests for PIN/OTP, suspicious domains, collect requests, and intent mismatch. Return only JSON matching the supplied schema. Include `plain_english` as a more detailed, calm explanation of what the user should understand and do. If a UPI ID, UPI URI, phone number, payee name, amount, note, or merchant code is visible, populate `upi_details` only with evidence from the input; use null for unknown fields. Never invent an identity. Keep the explanation plain English and actionable. Input:\n{content}"""

def extract_upi_details(content: str) -> Optional[UpiDetails]:
    """Extract evidence-backed UPI identity and payment fields from text or QR payloads."""
    raw = unquote(content or "")
    upi_id = None
    display_name = None
    phone_number = None
    amount = None
    currency = None
    note = None
    merchant_code = None
    uri_match = re.search(r"upi://pay\?[^\s]+", raw, flags=re.IGNORECASE)
    if uri_match:
        parsed = urlparse(uri_match.group(0))
        params = {key: values[0] for key, values in parse_qs(parsed.query).items() if values}
        upi_id = params.get("pa")
        display_name = params.get("pn")
        amount = params.get("am")
        currency = params.get("cu")
        note = params.get("tn")
        merchant_code = params.get("mc")
    if not upi_id:
        vpa_match = re.search(r"\b[\w.\-]{2,}@[a-zA-Z][\w.-]{2,}\b", raw)
        upi_id = vpa_match.group(0) if vpa_match else None
    phone_match = re.search(r"(?<!\d)(?:\+91[- .]?)?[6-9]\d{9}(?!\d)", raw)
    phone_number = phone_match.group(0) if phone_match else None
    if not any([upi_id, display_name, phone_number, amount, note, merchant_code]):
        return None
    confidence = "high" if upi_id and (display_name or amount or note) else "medium" if upi_id else "low"
    return UpiDetails(upi_id=upi_id, display_name=display_name, phone_number=phone_number, amount=amount, currency=currency, note=note, merchant_code=merchant_code, confidence=confidence)

async def call_gemini(input_type: str, content: str, image_bytes: Optional[bytes] = None, image_mime_type: Optional[str] = None) -> GeminiAssessment:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or genai is None or types is None:
        raise HTTPException(status_code=503, detail="Gemini analysis is not configured. Set GEMINI_API_KEY on Render.")
    logger.info("Sending structured semantic evaluation to Gemini", extra={"stage": "SEMANTIC_EVAL"})
    client = genai.Client(api_key=api_key)
    prompt = prompt_for(input_type, content)
    contents = prompt
    if image_bytes:
        image_part = types.Part.from_bytes(data=image_bytes, mime_type=image_mime_type or "image/jpeg")
        contents = [prompt, image_part]
        logger.info("Attached original image bytes for multimodal inspection", extra={"stage": "VISION_OCR"})
    response = await client.aio.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        contents=contents,
        config=types.GenerateContentConfig(
            temperature=0.1,
            response_mime_type="application/json",
            response_schema=GeminiAssessment,
        ),
    )
    assessment = response.parsed if getattr(response, "parsed", None) else GeminiAssessment.model_validate_json(response.text)
    logger.info("Gemini returned score=%s severity=%s", assessment.score, assessment.severity, extra={"stage": "SEMANTIC_EVAL"})
    return assessment

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "gemini": "configured" if os.getenv("GEMINI_API_KEY") else "missing"}

@app.post("/api/v1/analyze", response_model=AnalyzeResponse)
async def analyze(raw_request: Request, file: Optional[UploadFile] = File(default=None)) -> AnalyzeResponse:
    image_payload: Optional[bytes] = None
    image_mime_type: Optional[str] = None
    if file is not None:
        payload = await file.read()
        if len(payload) > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="Image exceeds 10 MB limit")
        logger.info("Image received: %s bytes, filename=%s", len(payload), file.filename, extra={"stage": "VISION_OCR"})
        try:
            image = Image.open(BytesIO(payload))
            image.load()
        except Exception as exc:
            logger.warning("Uploaded file could not be decoded as an image: %s", exc, extra={"stage": "VISION_OCR"})
            raise HTTPException(status_code=400, detail="Uploaded file is not a valid image") from exc

        qr_text: list[str] = []
        try:
            qr_text = [item.data.decode("utf-8", errors="replace").strip() for item in pyzbar.decode(image) if item.data.strip()]
            logger.info("Decoded %s QR/barcode payload(s)", len(qr_text), extra={"stage": "VISION_OCR"})
        except Exception as exc:
            logger.warning("QR/barcode decoding failed: %s", exc, extra={"stage": "VISION_OCR"})

        ocr_text = ""
        try:
            ocr_text = pytesseract.image_to_string(image).strip()
            logger.info("OCR extracted %s characters", len(ocr_text), extra={"stage": "VISION_OCR"})
        except Exception as exc:
            logger.warning("OCR extraction failed: %s", exc, extra={"stage": "VISION_OCR"})

        qr_evidence = " | ".join(qr_text) if qr_text else "none"
        ocr_evidence = ocr_text if ocr_text else "none"
        if not qr_text and not ocr_text:
            logger.warning("No machine-readable text or QR data found; continuing with visual inspection", extra={"stage": "VISION_OCR"})
        content = f"Image filename: {file.filename or 'uploaded-image'}\nQR code data found: {qr_evidence}\nOCR extracted text: {ocr_evidence}"
        input_type = "image"
        source = "manual"
        image_payload = payload
        image_mime_type = file.content_type if file.content_type and file.content_type.startswith("image/") else "image/jpeg"
    else:
        try:
            payload = AnalyzeRequest.model_validate(await raw_request.json())
        except Exception as exc:
            raise HTTPException(status_code=400, detail="Provide valid JSON content or an image file") from exc
        content = payload.content
        input_type = payload.input_type
        source = payload.source
        logger.info("%s payload received with %s characters", input_type, len(content), extra={"stage": "INGESTION"})

    if input_type == "url":
        urls = re.findall(r"https?://[^\s]+", content)
        logger.info("Extracted URLs: %s", urls, extra={"stage": "LINK_ANALYSIS"})
    assessment = await call_gemini(input_type, content, image_payload, image_mime_type)
    extracted_upi = extract_upi_details(content)
    if extracted_upi:
        model_upi = assessment.upi_details
        assessment.upi_details = UpiDetails(
            upi_id=extracted_upi.upi_id or (model_upi.upi_id if model_upi else None),
            display_name=extracted_upi.display_name or (model_upi.display_name if model_upi else None),
            phone_number=extracted_upi.phone_number or (model_upi.phone_number if model_upi else None),
            amount=extracted_upi.amount or (model_upi.amount if model_upi else None),
            currency=extracted_upi.currency or (model_upi.currency if model_upi else None),
            note=extracted_upi.note or (model_upi.note if model_upi else None),
            merchant_code=extracted_upi.merchant_code or (model_upi.merchant_code if model_upi else None),
            confidence=extracted_upi.confidence,
        )
    if not assessment.plain_english:
        assessment.plain_english = assessment.summary + " " + assessment.action_detail
    return AnalyzeResponse(**assessment.model_dump(), source=source, timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), trace_id=trace_context.get())
