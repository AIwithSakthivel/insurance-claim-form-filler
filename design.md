# Auto-Form Filler — Technical Design
**Project:** JS Windshields Insurance Claim Auto-Filler
**Version:** 1.0 (Prototype)
**Date:** March 2026

---

## 1. Architecture Overview

Two parallel implementations exist. Both produce identical output.

### Version 1 — Backend (FastAPI + Python)
```
Mobile Browser
     │
     ▼
FastAPI Server (laptop, port 8080)
     ├── POST /process
     │       ├── extractor.py  →  Claude Vision API
     │       ├── form_filler.py →  reportlab overlay
     │       └── returns filled PDF
     └── GET /  →  serves frontend/index.html
```

### Version 2 — Serverless (Pure HTML, recommended)
```
Mobile Browser
     ├── Loads index.html (from Netlify)
     ├── Fetches united_india_claim_form.pdf (from Netlify)
     ├── POST → api.anthropic.com  (Claude extraction)
     └── PDF filling via pdf-lib (runs in browser)
         → Download filled PDF (no server involved)
```

**v2 is the production recommendation** — no server to maintain, runs from any mobile browser, hosted as static files on Netlify (free). Domain jswindshields.com is registered on GoDaddy, nameservers point to Netlify.

---

## 2. File Structure

```
rupak/
├── backend/                        # Version 1 — Python backend
│   ├── main.py                     # FastAPI app, routes
│   ├── extractor.py                # Claude Vision extraction
│   ├── form_filler.py              # reportlab PDF overlay
│   ├── config.py                   # Static business constants
│   ├── requirements.txt
│   ├── .env                        # ANTHROPIC_API_KEY (gitignored)
│   ├── .env.example
│   └── analyze_coords.py           # One-time coordinate analysis tool
│
├── frontend/
│   ├── index.html                  # v1 frontend (served by FastAPI)
│   ├── claim_filler_v2.html        # v2 standalone app (upload to Hostinger)
│   └── united_india_claim_form.pdf # Blank form (upload to Hostinger)
│
├── forms/
│   └── united_india_claim_form.pdf # Blank claim form (used by backend)
│
├── JSWindshields_Instructions.txt  # Master business rules
├── govt_id.pdf                     # Sample combined govt ID (testing)
├── sample_filled_form_reference.pdf # Manually filled reference form
├── spec.md                         # Product specification
└── design.md                       # This file
```

---

## 3. PDF Coordinate System

The blank claim form is a **digitally created flat PDF** (not scanned).

```
Page size: 595.56 × 842.04 pts (A4)

PyMuPDF coords:    Origin top-left,    y increases downward
reportlab coords:  Origin bottom-left, y increases upward
pdf-lib coords:    Origin bottom-left, y increases upward  (same as reportlab)

Conversion:  rl_y = PAGE_H - pymupdf_y0 - 7
             (−7 accounts for font ascent at size 9)
```

Coordinates were derived by running `analyze_coords.py` (PyMuPDF text block extraction) against the blank form, giving exact (x, y) positions of every label. Field value positions are calculated relative to each label's end position.

---

## 4. Field Coordinate Map

All y values in reportlab / pdf-lib format (origin bottom-left).

| Field | x_left | x_right | y |
|-------|--------|---------|---|
| Policy No | 65 | 570 | 720.6 |
| Insured Name | 176 | 570 | 707.5 |
| Insured Address (line 1) | 182 | 570 | 692.2 |
| Pin Code | 158 | 250 | 646.7 |
| State | 283 | 570 | 646.7 |
| Aadhaar No | 162 | 290 | 620.1 |
| PAN No | 335 | 570 | 622.0 |
| Account No | 168 | 290 | 605.9 |
| Bank Name | 348 | 570 | 605.9 |
| IFSC Code | 175 | 290 | 592.9 |
| Branch Name | 356 | 570 | 592.9 |
| Registration No | 184 | 293 | 579.5 |
| Make | 327 | 408 | 579.5 |
| Model | 444 | 570 | 579.5 |
| Engine No | 162 | 293 | 565.6 |
| Chassis No | 346 | 570 | 565.6 |
| Date of Loss | 172 | 290 | 551.3 |
| Time | 322 | 398 | 551.3 |
| Place of Accident | 222 | 570 | 536.8 |
| Driver Name | 174 | 570 | 505.1 |
| DL No / Expiry | 248 | 570 | 492.4 |
| Accident Description (start) | 115 | 570 | 467.0 |
| No of Occupants | 220 | 290 | 423.4 |
| Workshop Name | 245 | 570 | 411.0 |
| Workshop Address | 245 | 570 | 401.5 |
| Workshop Mobile | 195 | 290 | 387.8 |
| Estimate Amount | 530 | 575 | 389.0 |
| Declaration Date | 47 | 200 | 95.1 |
| Declaration Place | 49 | 395 | 81.8 |

---

## 5. Yes/No Underline Positions

All Yes/No fields are always marked **No**. A filled black rectangle (1.5pt height) is drawn below the "No" text.

| Field | x_start | x_end | pymupdf_y1 |
|-------|---------|-------|------------|
| Theft of Vehicle | 205.7 | 217.4 | 470.6 |
| Theft of Accessories | 222.8 | 234.5 | 495.2 |
| Accident reported to police | 275.1 | 284.9 | 519.3 |
| Any Injury/Death to Driver | 247.0 | 256.8 | 548.3 |
| Any TP Injury/Death | 221.3 | 231.0 | 580.4 |
| Any Injury/Death to Occupant | 261.1 | 270.8 | 615.8 |
| Any TP Property Damage | 240.6 | 250.4 | 651.3 |

```
underline_y (pdf-lib) = PAGE_H − pymupdf_y1 − 5
rect: (x_start, underline_y − 1.5, width, 1.5)
```

---

## 6. AM/PM Underline Positions

| Option | x_start | x_end | pymupdf_y1 |
|--------|---------|-------|------------|
| A.M. | 400.2 | 419.4 | 293.7 |
| P.M. | 427.5 | 446.3 | 293.7 |

---

## 7. Text Rendering Rules

| Rule | Value |
|------|-------|
| Font | Helvetica (standard PDF font) |
| Main font size | 9pt |
| Workshop address font size | 8pt |
| Line leading | 11pt |
| Alignment | Horizontally centered within field bounds |
| Multi-line fields | Wrapped by word, centered per line |

**Centering formula:**
```
x = x_left + (field_width − text_width) / 2
if text_width >= field_width: x = x_left  (left-align fallback)
```

**Multi-line fields:**
- Insured Address: max 3 lines
- Place of Accident: max 2 lines
- Accident Description: max 4 lines

---

## 8. Claude Extraction

### Model
`claude-sonnet-4-20250514`

### Input
Combined govt ID PDF (RC, Insurance Policy, DL, Aadhaar, PAN, optional Estimate) sent as base64-encoded document.

### Output
JSON with 14 fields:
```json
{
  "policy_no": "",
  "insured_name": "",
  "insured_address": "",
  "pin_code": "",
  "aadhaar_no": "",
  "pan_no": "",
  "reg_no": "",
  "make": "",
  "model": "",
  "engine_no": "",
  "chassis_no": "",
  "driver_name": "",
  "dl_no": "",
  "dl_expiry": ""
}
```

### Key Extraction Rules
- `insured_name` → from RC (owner), not DL
- `driver_name` → from DL exclusively
- `insured_address` → street/locality only, no pin code, no state
- `dl_expiry` → LMV validity date preferred, format DD-MM-YYYY
- `aadhaar_no` → formatted with spaces (XXXX XXXX XXXX)
- Empty string `""` for any field not found

### Browser Call (v2)
```javascript
headers: {
  'x-api-key': apiKey,
  'anthropic-version': '2023-06-01',
  'content-type': 'application/json',
  'anthropic-dangerous-allow-browser': 'true'
}
```

---

## 9. PDF Filling — Implementation Comparison

| Aspect | v1 (Python) | v2 (JavaScript) |
|--------|-------------|-----------------|
| Library | reportlab + pypdf | pdf-lib |
| Where it runs | Server (laptop) | Browser (phone) |
| Coordinate origin | bottom-left | bottom-left |
| Text centering | `stringWidth()` | `font.widthOfTextAtSize()` |
| Overlay method | Canvas → PdfWriter.merge_page() | PDFDocument.load() → drawText() |
| Output | HTTP response (bytes) | Blob → createObjectURL() |

Coordinates are **identical** in both implementations since reportlab and pdf-lib share the same bottom-left origin and point units.

---

## 10. v2 Deployment — Netlify + GoDaddy

**Infrastructure:**
- Domain registrar: GoDaddy (`jswindshields.com`)
- Hosting: Netlify (free static hosting)
- GoDaddy nameservers point to Netlify

**Deploy folder structure:**
```
deploy/
└── auto-claim-form-filler/
    ├── index.html                  ← claim_filler_v2.html renamed
    └── united_india_claim_form.pdf
```

Drag and drop the `deploy/auto-claim-form-filler/` folder in Netlify dashboard.

**Access URL:** `https://jswindshields.com/auto-claim-form-filler/`

The blank form is fetched via a relative URL (`./united_india_claim_form.pdf`) at runtime. Both files must be in the same directory.

See `DEPLOY.md` for full step-by-step deployment instructions.

---

## 11. v1 Deployment — Local (Laptop)

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8080
```

Requires:
- `.env` file with `ANTHROPIC_API_KEY=sk-ant-...`
- All devices on same WiFi network
- Mac firewall to allow connections on port 8080

**Not recommended for production** — tied to laptop being on and connected.

---

## 12. API Key Management

| Version | Storage | Security |
|---------|---------|----------|
| v1 | `.env` file on laptop | Private, server-side |
| v2 | Browser `localStorage` | Exposed on device — acceptable for internal single-user tool |

---

## 13. Data Privacy

- No customer data is stored anywhere
- Claude API processes the PDF in-memory per request
- v2: Data never leaves the browser except for the Claude API call
- v1: Data passes through the laptop server but is not persisted

---

## 14. Adding the TVM Branch (Future)

To support Tiruvannamalai 2-page form:
1. Run `analyze_coords.py` against TVM blank form to get coordinates
2. Add a separate coordinate map in `form_filler.py` / `claim_filler_v2.html`
3. Add branch selector in UI
4. Route to correct coordinate map based on branch selection
5. Upload TVM blank form PDF to Hostinger

---

## 15. Dependencies

### Python (v1)
```
anthropic>=0.86.0
fastapi>=0.110.0
uvicorn>=0.29.0
python-multipart>=0.0.9
reportlab>=4.0.0
pypdf>=4.0.0
pymupdf>=1.24.0
python-dotenv>=1.0.0
```

### JavaScript (v2)
```
pdf-lib@1.17.1  (via unpkg CDN)
Anthropic API   (direct HTTPS fetch)
```
No build step. No npm. No framework.
