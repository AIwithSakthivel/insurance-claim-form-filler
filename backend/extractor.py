"""Extract fields from combined govt ID PDF using Claude Vision."""
import json
import anthropic
from dotenv import load_dotenv

load_dotenv()


EXTRACTION_PROMPT = """You are an expert at extracting information from Indian vehicle documents.

The uploaded PDF contains multiple documents: Insurance Policy, RC (Registration Certificate),
Driving Licence (DL), PAN Card, Aadhaar Card, and possibly an Estimate sheet.

Extract the following fields and return ONLY a valid JSON object with these exact keys.
Use empty string "" if a field is not found.

{
  "policy_no": "from Insurance Policy schedule",
  "insured_name": "owner name from RC (not DL). Use title case.",
  "insured_address": "street address from RC or Aadhaar — exclude pin code and state",
  "pin_code": "6-digit pin code from address",
  "aadhaar_no": "12-digit Aadhaar number (with spaces as on card, e.g. 4652 5132 7631)",
  "pan_no": "PAN number (e.g. ETBPP5984C)",
  "reg_no": "vehicle registration number from RC (e.g. TN 29 DZ 2342)",
  "make": "vehicle maker from RC (e.g. ASHOK LEYLAND)",
  "model": "vehicle model from RC (e.g. BADA DOST 12TNDD)",
  "engine_no": "engine number from RC",
  "chassis_no": "chassis number from RC",
  "driver_name": "name from Driving Licence ONLY (not RC owner)",
  "dl_no": "DL number (e.g. TN29T20060001094)",
  "dl_expiry": "DL valid till date — use LMV validity if multiple types (format DD-MM-YYYY)"
}

Rules:
- insured_address must NOT include pin code or state — only street/locality/city
- state is always Tamil Nadu — do not extract it
- driver_name comes ONLY from the Driving Licence, not the RC
- For dl_expiry, prefer the LMV (Light Motor Vehicle) validity date
- Return ONLY the JSON object, no markdown fences, no explanation"""


def extract_fields(pdf_bytes: bytes) -> dict:
    client = anthropic.Anthropic()

    import base64
    pdf_b64 = base64.standard_b64encode(pdf_bytes).decode("utf-8")

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": EXTRACTION_PROMPT,
                    },
                ],
            }
        ],
    )

    raw = response.content[0].text.strip()
    # Strip markdown fences if Claude wraps in them despite instructions
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())
