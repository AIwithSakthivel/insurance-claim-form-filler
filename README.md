# JS Windshields Auto-Form Filler

A smart automation tool built for **JS Windshields (Dharmapuri, Tamil Nadu)** to speed up motor insurance claim form preparation.

The app extracts customer data from uploaded government documents (RC, DL, Aadhaar, PAN, Insurance Policy) using Claude, and generates a filled claim form PDF.

## Problem It Solves
Manual transfer of details from multiple physical documents to insurer claim forms is slow and error-prone. This tool automates extraction and form filling to reduce turnaround time per customer.

## Features
- AI-powered document extraction from combined uploaded PDF files.
- Extraction prompt rules to separate owner details (RC/Policy) and driver details (DL).
- Claim logic support for cashless/non-cashless flow and preset accident descriptions.
- Form filling pipeline with deterministic PDF coordinates.
- Mobile-friendly single-page interface for workshop staff.

## Tech Stack
- Backend: Python, FastAPI, Uvicorn
- AI integration: Anthropic Claude API (`claude-sonnet-4-20250514`)
- PDF processing: `reportlab`, `pypdf`, `PyMuPDF`
- Frontend: HTML + JavaScript (served by FastAPI)
- Deployment: Railway (recommended), Render (supported)

## Project Structure
```text
.
├── backend/
│   ├── main.py
│   ├── extractor.py
│   ├── form_filler.py
│   ├── config.py
│   └── requirements.txt
├── frontend/
│   └── claim_filler_v2.html
├── claim_forms/
├── logo/
├── Instructions/
├── render.yaml
└── spec.md / design.md
```

## Local Setup

### Prerequisites
- Python 3.9+
- Anthropic API key

### Install and Run
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd claim-form-generator
   ```
2. Create local env file:
   ```bash
   touch backend/.env
   ```
3. Add your key to `backend/.env`:
   ```env
   API_KEY=your_claude_api_key_here
   ```
4. Install dependencies and start server:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --host 0.0.0.0 --port 8080 --reload
   ```
5. Open:
   - `http://localhost:8080`

## API Endpoints
- `GET /` - Serves frontend UI.
- `POST /extract` - Extracts structured fields from uploaded govt-id PDF.
- `POST /process` - Backend extraction + backend PDF fill; returns filled PDF.
- `GET /health` - Health check.

## Deployment

### Railway (Recommended)
1. Push this repository to GitHub.
2. In Railway, create a project from the GitHub repo.
3. Configure service settings:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variable:
   - `API_KEY=<your_anthropic_key>`
5. Deploy and open the Railway URL.
6. If you keep Root Directory as repository root, use:
   - Start Command: `uvicorn --app-dir backend main:app --host 0.0.0.0 --port $PORT`

### Render (Alternative)
1. Connect repository to Render.
2. Create a Blueprint instance (uses `render.yaml`).
3. Set environment variable:
   - `API_KEY=<your_anthropic_key>`

## Security Notes
- Keep `backend/.env` local only; do not commit secrets.
- In production, always set secrets in the platform dashboard (Railway/Render env vars), not in Git.

## Current Limitations
- Hardcoded for Dharmapuri branch workflow.
- Coordinate mapping is not insurer-specific yet.
- Public API has no authentication/rate limiting yet.

## Future Scope
- Insurer-specific coordinate maps.
- Multi-branch support.
- API authentication and rate limiting.
- Expanded extraction schema for commercial vehicle fields.

---
**Developer:** Sakthivel Thangaraj  
**Client:** JS Windshields
