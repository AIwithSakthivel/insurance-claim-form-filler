# Auto-Form Filler - Technical Design
**Project:** JS Windshields Insurance Claim Auto-Filler  
**Scope:** Backend implementation + business instruction alignment  
**Version:** 2.0 (As Implemented)  
**Date:** March 31, 2026

---

## 1. Purpose

This document describes the **current backend design in this repository** and how it aligns with `Instructions/JSWindshields_Instructions.txt`.

It is implementation-first: all sections reflect actual code under `backend/` and actual assets in this repo.

---

## 2. Current Architecture (As-Is)

Two execution paths exist today:

### Path A: Backend-assisted browser flow (default in `frontend/claim_filler_v2.html`)

```text
User (mobile/desktop browser)
  -> GET /                     (FastAPI serves frontend)
  -> POST /extract             (FastAPI calls Claude, returns JSON)
  -> Browser fills PDF via pdf-lib using /claim_forms/<insurer>.pdf
  -> Browser downloads filled PDF
```

### Path B: Full backend fill flow (`POST /process`)

```text
User client
  -> POST /process             (PDF + form inputs)
      -> extractor.extract_fields()   [Claude]
      -> form_filler.fill_form()      [reportlab overlay + pypdf merge]
  <- application/pdf (filled form bytes)
```

FastAPI also serves static assets:
- `/static` -> `frontend/`
- `/claim_forms` -> `claim_forms/`
- `/logo` -> `logo/`

---

## 3. Actual Repository Layout

```text
.
├── backend/
│   ├── main.py
│   ├── extractor.py
│   ├── form_filler.py
│   ├── config.py
│   ├── requirements.txt
│   └── .env
├── Instructions/
│   └── JSWindshields_Instructions.txt
├── frontend/
│   └── claim_filler_v2.html
├── claim_forms/
│   ├── Cholamandalam-Claim-Form.pdf
│   ├── Generali-Central-Claim-Form.pdf
│   ├── HDFC-ERGO-Claim-Form.pdf
│   ├── Kotak-Mahindra-Claim-Form.pdf
│   ├── Liberty-General-Claim-Form.pdf
│   ├── Magma-HDI-Claim-Form.pdf
│   ├── Reliance-General-Claim-Form.pdf
│   ├── Royal-Sundaram-Claim-Form.pdf
│   ├── SBI-General-Claim-Form.pdf
│   ├── Shriram-General-Claim-Form.pdf
│   ├── TATA-AIG-Claim-Form.pdf
│   ├── United-India-Claim-Form.pdf
│   └── Universal-Sompo-Claim-Form.pdf
├── logo/JSWINDSHIELDSLOGO.png
├── render.yaml
├── spec.md
└── design.md
```

---

## 4. Backend Component Design

## 4.1 `backend/main.py`
Responsibilities:
- Boot FastAPI app and CORS middleware (`allow_origins=["*"]`).
- Load `.env` and enforce `ANTHROPIC_API_KEY` presence for extraction routes.
- Serve frontend and static claim form assets.
- Expose API routes:
  - `GET /` -> serves `frontend/claim_filler_v2.html`
  - `POST /extract` -> extraction-only endpoint
  - `POST /process` -> extraction + PDF fill endpoint
  - `GET /health` -> basic health status

## 4.2 `backend/extractor.py`
Responsibilities:
- Convert uploaded PDF bytes to base64.
- Call Anthropic Messages API with model `claude-sonnet-4-20250514`.
- Send a strict extraction prompt with JSON-only response instructions.
- Parse model output into dict; strips markdown fences defensively before `json.loads`.

Extracted keys:
- `policy_no`, `insured_name`, `insured_address`, `pin_code`
- `aadhaar_no`, `pan_no`
- `reg_no`, `make`, `model`, `engine_no`, `chassis_no`
- `driver_name`, `dl_no`, `dl_expiry`

## 4.3 `backend/form_filler.py`
Responsibilities:
- Build a reportlab overlay page using fixed coordinates.
- Merge overlay onto selected insurer PDF page 1 using `pypdf`.
- Return resulting PDF bytes.

Key behaviors:
- Uses Helvetica, size 9 (workshop name/address size 8).
- Centers text within field bounds.
- Wraps long text for address/place/accident description.
- Always fills `State = Tamil Nadu`.
- Cashless flow fills bank fields; non-cashless keeps them blank.
- Underlines selected `AM` or `PM`.
- Underlines `No` for all Yes/No questions.
- Auto-fills declaration date with `date.today()` and place from config (`Dharmapuri`).

## 4.4 `backend/config.py`
Responsibilities:
- Stores static business constants:
  - Workshop identity (Dharmapuri)
  - Bank details
  - Declaration place
  - Accident description templates
  - Occupants mapping by accident type

---

## 5. API Contract

## 5.1 `POST /extract`
**Input (`multipart/form-data`)**
- `govt_id_pdf` (required, `.pdf` only)

**Output (`application/json`)**
- Extracted field dict (14 keys listed above)

**Errors**
- `500` if `ANTHROPIC_API_KEY` missing
- `400` for non-PDF upload
- `500` for extraction/model/parsing failure

## 5.2 `POST /process`
**Input (`multipart/form-data`)**
- `govt_id_pdf` (required)
- `cashless` (`cashless` | `non-cashless`)
- `insurer_file` (filename from `claim_forms/`)
- `accident_date` (`DD/MM/YYYY`)
- `accident_time` (`HH:MM` in 12h-style value expected by form)
- `am_pm` (`AM` | `PM`)
- `accident_place` (text)
- `accident_type` (`stone_hit` | `branch_moving` | `branch_parked`)
- `estimate_amount` (optional)

**Server-derived values**
- `accident_description` from `ACCIDENT_DESCRIPTIONS[accident_type]`
- `occupants` from `OCCUPANTS[accident_type]`

**Output**
- `application/pdf` with header: `attachment; filename=filled_claim_form.pdf`

## 5.3 `GET /health`
Output:
```json
{"status": "ok"}
```

---

## 6. PDF Layout and Rendering Rules

## 6.1 Coordinate System
- Target page constants in code:
  - `PAGE_W = 595.56`
  - `PAGE_H = 842.04`
- Conversion helper:
  - `rl_y = PAGE_H - pymupdf_y0 - 7`

## 6.2 Typography and alignment
- Font: Helvetica
- Default size: 9
- Workshop size: 8
- Line spacing (`LEADING`): 11
- Horizontal alignment: centered in each `[x_left, x_right]` box
- Overflow behavior: if text width exceeds box width, left fallback at `x_left`

## 6.3 Wrapped fields
- Insured address: max 3 lines
- Accident place: max 2 lines
- Accident description: max 4 lines

## 6.4 Yes/No and AM/PM markings
- Yes/No items are rendered as black underline rectangles under `No` positions.
- AM/PM rendered as underline below selected token.

---

## 7. Instruction Alignment Matrix

| Instruction Rule | Status in Current Code | Notes |
|---|---|---|
| State must be `Tamil Nadu` | Implemented | Hardcoded in PDF fill path. |
| Text center aligned, size 9 | Implemented | Centering helper + font size defaults. |
| Workshop address size 8 | Implemented | `FONT_SIZE_WORKSHOP = 8`. |
| Cashless -> fill bank details | Implemented | Conditional in form fill logic. |
| Non-cashless -> leave bank blank | Implemented | Same conditional. |
| All Yes/No -> mark No | Implemented | `YES_NO_UNDERLINES` loop. |
| Underline AM/PM | Implemented | `AM_COORDS` / `PM_COORDS`. |
| Driver details from DL only | Implemented in prompt intent | Enforced by extraction prompt, not deterministic parser logic. |
| Policy no from insurance doc | Implemented in prompt intent | Prompt directs model source. |
| Use reportlab overlay (printable) | Implemented in backend `/process` | Browser flow also exists via `pdf-lib`. |
| Phone browser usability | Implemented | Frontend is mobile-first single page. |
| Success/error sounds | Implemented in frontend | Matches instruction behavior. |

---

## 8. Gaps Between Instruction File and Implementation

1. Branch selection (Dharmapuri/Tiruvannamalai) is not implemented in backend; config is fixed to Dharmapuri values.
2. Instruction says each insurer requires unique coordinates; current backend reuses one coordinate map for all insurer PDFs.
3. Extraction rules mention additional commercial-vehicle fields (FC/permit/tax); backend extraction schema does not include them.
4. Current default frontend path uses `/extract` + browser fill; `/process` exists but is not the primary UI path.
5. `insurer_file` is accepted directly and joined as a path; there is no backend whitelist validation.
6. API has open CORS and no auth/rate limiting.

---

## 9. Runtime and Deployment

## 9.1 Python dependencies
- anthropic
- fastapi
- uvicorn
- python-multipart
- reportlab
- pypdf
- pymupdf
- python-dotenv

## 9.2 Local run
From `backend/`:
```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8080
```

## 9.3 Render deployment
`render.yaml` config:
- `rootDir: backend`
- build: `pip install -r requirements.txt`
- start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- env var required: `ANTHROPIC_API_KEY`

---

## 10. Recommended Next Engineering Steps

1. Add strict backend whitelist for `insurer_file` against known files in `claim_forms/`.
2. Split form coordinate maps by insurer and select map dynamically.
3. Extend extraction schema for commercial vehicle fields listed in instructions.
4. Add validation and normalization for date/time/amount inputs at API boundary.
5. Add authentication and restrict CORS before internet-facing production rollout.
6. Add automated regression checks for coordinate overflow and clipping per insurer form.

---

## 11. Design Decision Summary

- Extraction is delegated to Claude Sonnet with a strict JSON schema prompt.
- Rendering is deterministic coordinate-based overlay for print-ready output.
- Business constants are centralized in `config.py`.
- System currently favors rapid operational use for Dharmapuri workflow, with clear extension points for branch expansion and insurer-specific precision.
