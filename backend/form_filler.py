"""
Fill the United India Motor OD Claim Form (Dharmapuri branch) using reportlab overlay.

Coordinate system: reportlab uses origin at bottom-left.
All y values below are derived from PyMuPDF analysis of the blank PDF.
Page size: 595.56 x 842.04 pts
"""
import io
from datetime import date
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from pypdf import PdfReader, PdfWriter

from config import (
    CLAIM_FORMS_DIR,
    WORKSHOP_NAME,
    WORKSHOP_ADDRESS,
    WORKSHOP_MOBILE,
    BANK_ACCOUNT_NO,
    BANK_NAME,
    BANK_IFSC,
    BANK_BRANCH,
    DECLARATION_PLACE,
    ACCIDENT_DESCRIPTIONS,
    OCCUPANTS,
)

PAGE_W = 595.56
PAGE_H = 842.04
FONT = "Helvetica"
FONT_SIZE = 9
FONT_SIZE_WORKSHOP = 8
LEADING = 11  # line spacing


def _rl_y(pymupdf_y0: float) -> float:
    """Convert PyMuPDF top-of-text y to reportlab baseline y."""
    return PAGE_H - pymupdf_y0 - 7


def _center_x(text: str, x_left: float, x_right: float, size: float = FONT_SIZE) -> float:
    """Return x to draw text centered between x_left and x_right."""
    w = stringWidth(text, FONT, size)
    available = x_right - x_left
    if w >= available:
        return x_left
    return x_left + (available - w) / 2


def _wrap(text: str, max_width: float, size: float = FONT_SIZE) -> list[str]:
    """Wrap text to fit within max_width, return list of lines."""
    words = text.split()
    lines, current = [], ""
    for word in words:
        candidate = f"{current} {word}".strip() if current else word
        if stringWidth(candidate, FONT, size) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _draw_centered(c: canvas.Canvas, text: str, x_left: float, x_right: float,
                   y: float, size: float = FONT_SIZE):
    c.setFont(FONT, size)
    x = _center_x(text, x_left, x_right, size)
    c.drawString(x, y, text)


def _draw_wrapped_centered(c: canvas.Canvas, text: str, x_left: float, x_right: float,
                           y_start: float, max_lines: int = 4, size: float = FONT_SIZE) -> float:
    """Draw wrapped text, each line centered. Returns y after last line."""
    lines = _wrap(text, x_right - x_left, size)
    y = y_start
    for i, line in enumerate(lines[:max_lines]):
        _draw_centered(c, line, x_left, x_right, y, size)
        y -= LEADING
    return y


def _underline_no(c: canvas.Canvas, x0: float, x1: float, rl_bottom: float):
    """Draw a filled black rectangle underline below 'No' text."""
    c.setFillColorRGB(0, 0, 0)
    c.rect(x0, rl_bottom - 2, x1 - x0, 1.5, fill=1, stroke=0)


def _underline_ampm(c: canvas.Canvas, x0: float, x1: float, rl_bottom: float):
    """Draw underline below AM or PM text."""
    c.setFillColorRGB(0, 0, 0)
    c.rect(x0, rl_bottom - 2, x1 - x0, 1.5, fill=1, stroke=0)


# ---------------------------------------------------------------------------
# Exact field coordinates derived from PyMuPDF analysis
# Format: (x_left, x_right, rl_y)  — where rl_y = _rl_y(pymupdf_y0)
# ---------------------------------------------------------------------------

# Pre-computed rl_y values (PAGE_H - pymupdf_y0 - 7):
# Policy No:           _rl_y(114.4) = 720.6
# Insured Name:        _rl_y(127.5) = 707.5
# Insured Address:     _rl_y(142.8) = 692.2
# Pin Code:            _rl_y(188.3) = 646.7
# Aadhar No:           _rl_y(214.9) = 620.1
# PAN No:              _rl_y(213.0) = 622.0
# Account No:          _rl_y(229.1) = 605.9
# IFSC Code:           _rl_y(242.1) = 592.9
# Reg No:              _rl_y(255.5) = 579.5
# Engine No:           _rl_y(269.4) = 565.6
# Date of Loss:        _rl_y(283.7) = 551.3
# Time:                _rl_y(283.7) = 551.3
# Place of Accident:   _rl_y(298.2) = 536.8
# Driver Name:         _rl_y(329.9) = 505.1
# DL No/Expiry:        _rl_y(342.6) = 492.4
# Accident Desc:       _rl_y(368.0) = 467.0  (start of description box)
# Occupants:           _rl_y(411.6) = 423.4
# Workshop Name:       _rl_y(426.2) = 408.8
# Workshop Mobile:     _rl_y(447.2) = 387.8
# Estimate:            _rl_y(446.0) = 389.0
# Declaration Date:    _rl_y(739.9) = 95.1
# Declaration Place:   _rl_y(753.2) = 81.8

# Yes/No underline positions — (x0, x1, rl_bottom)
# rl_bottom = PAGE_H - y1 (bottom of text in PyMuPDF)
# Then underline drawn at rl_bottom - 2

YES_NO_UNDERLINES = {
    # (x0_of_No, x1_of_No, pymupdf_y1)
    "theft_vehicle":    (205.7, 217.4, 470.6),   # "No" from "Theft of Vehicle: Yes / No"
    "theft_accessories":(222.8, 234.5, 495.2),   # "No" from "Theft of Accessories: Yes / No"
    # "Yes/No" as single tokens — estimated "No" portion (last 2/6 of width)
    "fir_reported":     (275.1, 284.9, 519.3),   # "No" within "Yes/No" token
    "driver_injury":    (247.0, 256.8, 548.3),
    "tp_injury":        (221.3, 231.0, 580.4),
    "occupant_injury":  (261.1, 270.8, 615.8),
    "tp_property":      (240.6, 250.4, 651.3),
}

AM_COORDS = (400.2, 419.4, 293.7)   # (x0, x1, pymupdf_y1)
PM_COORDS = (427.5, 446.3, 293.7)


def _build_overlay(data: dict) -> bytes:
    """Create the overlay PDF with all filled values."""
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(PAGE_W, PAGE_H))
    c.setFont(FONT, FONT_SIZE)
    c.setFillColorRGB(0, 0, 0)

    def draw(text, x_left, x_right, rl_y, size=FONT_SIZE):
        if text:
            _draw_centered(c, str(text), x_left, x_right, rl_y, size)

    # ── Policy No ──────────────────────────────────────────────────────────
    draw(data.get("policy_no"), 65, 570, 720.6)

    # ── Insured Details ────────────────────────────────────────────────────
    draw(data.get("insured_name"), 176, 570, 707.5)

    # Address: multi-line, wrap within cell
    address = data.get("insured_address", "")
    if address:
        _draw_wrapped_centered(c, address, 182, 570, 692.2, max_lines=3)

    draw(data.get("pin_code"), 158, 250, 646.7)
    draw("Tamil Nadu", 283, 570, 646.7)           # State: always Tamil Nadu

    # Mobile: skipped per instructions for this prototype

    draw(data.get("aadhaar_no"), 162, 290, 620.1)
    draw(data.get("pan_no"), 335, 570, 622.0)

    # ── Bank Account Details ───────────────────────────────────────────────
    if data.get("cashless"):
        draw(BANK_ACCOUNT_NO, 168, 290, 605.9)
        draw(BANK_NAME,       348, 570, 605.9)
        draw(BANK_IFSC,       175, 290, 592.9)
        draw(BANK_BRANCH,     356, 570, 592.9)

    # ── Vehicle Details ────────────────────────────────────────────────────
    draw(data.get("reg_no"),    184, 293, 579.5)
    draw(data.get("make"),      327, 408, 579.5)
    draw(data.get("model"),     444, 570, 579.5)
    draw(data.get("engine_no"), 162, 293, 565.6)
    draw(data.get("chassis_no"),346, 570, 565.6)

    # ── Date & Place of Loss ───────────────────────────────────────────────
    draw(data.get("accident_date"), 172, 290, 551.3)
    draw(data.get("accident_time"), 322, 398, 551.3)

    # AM / PM underline
    am_pm = data.get("am_pm", "AM").upper()
    if am_pm == "AM":
        x0, x1, py1 = AM_COORDS
        _underline_ampm(c, x0, x1, PAGE_H - py1)
    else:
        x0, x1, py1 = PM_COORDS
        _underline_ampm(c, x0, x1, PAGE_H - py1)

    # Place of accident: may need wrapping
    place = data.get("accident_place", "")
    if place:
        _draw_wrapped_centered(c, place, 222, 570, 536.8, max_lines=2)

    # ── Driver Details ─────────────────────────────────────────────────────
    draw(data.get("driver_name"), 174, 570, 505.1)
    dl_combined = ""
    if data.get("dl_no") and data.get("dl_expiry"):
        dl_combined = f"{data['dl_no']} & {data['dl_expiry']}"
    elif data.get("dl_no"):
        dl_combined = data["dl_no"]
    draw(dl_combined, 248, 570, 492.4)

    # ── Accident Description ───────────────────────────────────────────────
    desc = data.get("accident_description", "")
    if desc:
        _draw_wrapped_centered(c, desc, 115, 570, 467.0, max_lines=4)

    # ── No of Occupants ────────────────────────────────────────────────────
    draw(data.get("occupants", ""), 220, 290, 423.4)

    # ── Workshop Details ───────────────────────────────────────────────────
    # Workshop name + address (font size 8 per instructions)
    c.setFont(FONT, FONT_SIZE_WORKSHOP)
    _draw_centered(c, WORKSHOP_NAME, 245, 570, 411.0, FONT_SIZE_WORKSHOP)
    _draw_centered(c, WORKSHOP_ADDRESS, 245, 570, 401.5, FONT_SIZE_WORKSHOP)
    c.setFont(FONT, FONT_SIZE)

    draw(WORKSHOP_MOBILE, 195, 290, 387.8)

    estimate = data.get("estimate_amount", "")
    if estimate:
        draw(str(estimate), 530, 575, 389.0)

    # ── Yes/No Fields — all marked "No" ───────────────────────────────────
    for key, (x0, x1, py1) in YES_NO_UNDERLINES.items():
        rl_bottom = PAGE_H - py1
        _underline_no(c, x0, x1, rl_bottom)

    # ── Declaration ────────────────────────────────────────────────────────
    today = date.today().strftime("%d/%m/%Y")
    draw(today, 47, 200, 95.1)
    draw(DECLARATION_PLACE, 49, 395, 81.8)

    c.save()
    packet.seek(0)
    return packet.read()


def fill_form(data: dict, insurer_file: str) -> bytes:
    """
    Merge the overlay with the selected insurer's blank form and return filled PDF bytes.

    data dict keys:
        policy_no, insured_name, insured_address, pin_code,
        aadhaar_no, pan_no, reg_no, make, model, engine_no, chassis_no,
        driver_name, dl_no, dl_expiry,
        accident_date, accident_time, am_pm, accident_place,
        accident_description, occupants,
        cashless (bool), estimate_amount
    insurer_file: filename from claim_forms/ e.g. "United-India-Claim-Form.pdf"
    """
    form_path = CLAIM_FORMS_DIR / insurer_file
    overlay_bytes = _build_overlay(data)

    reader = PdfReader(str(form_path))
    overlay_reader = PdfReader(io.BytesIO(overlay_bytes))

    writer = PdfWriter()
    page = reader.pages[0]
    page.merge_page(overlay_reader.pages[0])
    writer.add_page(page)

    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()
