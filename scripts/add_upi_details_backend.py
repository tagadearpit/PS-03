from pathlib import Path
path = Path(__file__).parents[1] / "backend/app/main.py"
text = path.read_text()
text = text.replace('import re\nimport time', 'import re\nimport time\nfrom urllib.parse import parse_qs, unquote, urlparse')
text = text.replace('class GeminiAssessment(BaseModel):\n', '''class UpiDetails(BaseModel):
    upi_id: Optional[str] = None
    display_name: Optional[str] = None
    phone_number: Optional[str] = None
    amount: Optional[str] = None
    currency: Optional[str] = None
    note: Optional[str] = None
    merchant_code: Optional[str] = None
    confidence: str = Field(default="low", pattern="^(low|medium|high)$")

class GeminiAssessment(BaseModel):
''')
text = text.replace('    threats: list[Threat]\n\nclass AnalyzeResponse', '    threats: list[Threat]\n    upi_details: Optional[UpiDetails] = None\n    plain_english: str = ""\n\nclass AnalyzeResponse')
text = text.replace('Return only JSON matching the supplied schema. Keep the explanation plain English and actionable.', 'Return only JSON matching the supplied schema. Include `plain_english` as a more detailed, calm explanation of what the user should understand and do. If a UPI ID, UPI URI, phone number, payee name, amount, note, or merchant code is visible, populate `upi_details` only with evidence from the input; use null for unknown fields. Never invent an identity. Keep the explanation plain English and actionable.')
marker = 'async def call_gemini(input_type: str, content: str, image_bytes: Optional[bytes] = None, image_mime_type: Optional[str] = None) -> GeminiAssessment:\n'
helper = '''def extract_upi_details(content: str) -> Optional[UpiDetails]:
    """Extract evidence-backed UPI identity and payment fields from text or QR payloads."""
    raw = unquote(content or "")
    upi_id = None
    display_name = None
    phone_number = None
    amount = None
    currency = None
    note = None
    merchant_code = None
    uri_match = re.search(r"upi://pay\\?[^\\s]+", raw, flags=re.IGNORECASE)
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
        vpa_match = re.search(r"\\b[\\w.\\-]{2,}@[a-zA-Z][\\w.-]{2,}\\b", raw)
        upi_id = vpa_match.group(0) if vpa_match else None
    phone_match = re.search(r"(?<!\\d)(?:\\+91[- .]?)?[6-9]\\d{9}(?!\\d)", raw)
    phone_number = phone_match.group(0) if phone_match else None
    if not any([upi_id, display_name, phone_number, amount, note, merchant_code]):
        return None
    confidence = "high" if upi_id and (display_name or amount or note) else "medium" if upi_id else "low"
    return UpiDetails(upi_id=upi_id, display_name=display_name, phone_number=phone_number, amount=amount, currency=currency, note=note, merchant_code=merchant_code, confidence=confidence)

'''
if marker not in text: raise SystemExit('call_gemini marker not found')
text = text.replace(marker, helper + marker)
old = '    assessment = await call_gemini(input_type, content, image_payload, image_mime_type)\n    return AnalyzeResponse(**assessment.model_dump(), source=source, timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), trace_id=trace_context.get())'
new = '''    assessment = await call_gemini(input_type, content, image_payload, image_mime_type)
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
    return AnalyzeResponse(**assessment.model_dump(), source=source, timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), trace_id=trace_context.get())'''
if old not in text: raise SystemExit('response return not found')
path.write_text(text.replace(old, new))
print('backend UPI details added')
