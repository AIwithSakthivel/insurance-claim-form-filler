# Auto-Form Filler — Product Specification
**Client:** JS Windshields, Dharmapuri, Tamil Nadu
**Proprietor:** Rupak Kumar
**Version:** 1.0 (Prototype)
**Date:** March 2026

---

## 1. Problem Statement

Insurance claim filing for windshield repairs involves manually copying customer data from multiple government documents (RC, DL, Aadhaar, PAN, Insurance Policy) onto a paper claim form. This is error-prone, time-consuming, and done by hand for every customer.

The goal is to automate this: upload all customer documents as a single PDF, answer a few accident-specific questions, and get a filled, print-ready claim form instantly.

---

## 2. Scope (v1 Prototype)

### In Scope
- United India Insurance Motor OD Claim Form — Dharmapuri branch (1-page)
- Document types: RC, Insurance Policy, Driving Licence, Aadhaar, PAN
- Accident types: stone hit, tree branch (moving), tree branch (parked)
- Cashless and non-cashless claim flows
- Mobile browser usage
- Single-user (Rupak Kumar / branch staff)

### Out of Scope (deferred)
- Tiruvannamalai (TVM) branch 2-page form
- Chat / Q&A with LLM during form filling
- Work order management
- Multi-user / authentication
- RC-less or policy-less document sets

---

## 3. Users

| User | Role | Device |
|------|------|--------|
| Rupak Kumar | Proprietor — primary user | Mobile phone |
| Karthi | Branch Manager | Mobile phone |
| Prakash | Branch Associate | Mobile phone |

---

## 4. User Flow

```
1. Open app on mobile browser
2. Upload combined govt ID PDF (RC + Insurance + DL + Aadhaar + PAN)
3. Select:
   - Claim Type: Cashless / Non-Cashless
   - Accident Date & Time (AM/PM)
   - Place of Accident
   - Accident Type (stone hit / branch moving / branch parked)
   - Estimate Amount (optional)
4. Tap "Generate Filled Form"
5. App extracts all fields from documents via Claude AI
6. App fills the blank claim form PDF
7. Tap "Download" → save to phone
8. Print the filled PDF
```

---

## 5. Form Fields & Data Sources

### Fields Extracted by Claude (from govt ID PDF)

| Form Field | Source Document | Notes |
|------------|----------------|-------|
| Policy No | Insurance Policy | Schedule page |
| Insured Name | RC (owner name) | Title case |
| Insured Address | RC / Aadhaar | Excludes pin & state |
| Pin Code | RC / Aadhaar | 6 digits |
| Aadhaar No | Aadhaar card | Format: XXXX XXXX XXXX |
| PAN No | PAN card | e.g. ETBPP5984C |
| Registration No | RC | e.g. TN 29 DZ 2342 |
| Make | RC | e.g. ASHOK LEYLAND |
| Model | RC | e.g. BADA DOST 12TNDD |
| Engine No | RC | |
| Chassis No | RC | |
| Driver Name | Driving Licence ONLY | Not from RC |
| DL No / Expiry | Driving Licence | LMV validity preferred |

### Fields from User Input (UI)

| Form Field | UI Control |
|------------|-----------|
| Accident Date | Date picker |
| Accident Time | Time picker |
| AM / PM | Toggle |
| Place of Accident | Text input |
| Estimate Amount | Text input (optional) |
| Claim Type | Toggle (Cashless / Non-Cashless) |
| Accident Type | Radio (3 options) |

### Fields Hardcoded (Static Business Rules)

| Form Field | Value |
|------------|-------|
| State | Tamil Nadu (always — never "TN") |
| Workshop Name | JS WINDSHIELDS |
| Workshop Address | 5/215, Sagadevan Complex, Dharmapuri - 636705 |
| Workshop Mobile | 9080742507 |
| Bank Account No | 259080742507 (cashless only) |
| Bank Name | INDUSIND BANK (cashless only) |
| IFSC Code | INDB0000202 (cashless only) |
| Branch Name | DHARMAPURI (cashless only) |
| Declaration Place | Dharmapuri |
| Declaration Date | Today's date (auto) |
| All Yes/No fields | No (underlined) |
| Occupants (moving) | 1 |
| Occupants (parked) | 0 |

---

## 6. Accident Description Templates

| Type | Description |
|------|-------------|
| Stone hit | "While the vehicle was in motion, a flying stone projected from a preceding moving truck struck the front windshield, resulting in damage." |
| Tree branch — moving | "A tree branch fell onto the front windshield while the vehicle was in motion, causing damage." |
| Tree branch — parked | "A tree branch fell onto the front windshields while the vehicle was parked, causing damage." |

---

## 7. Form Filling Rules

| Rule | Behaviour |
|------|-----------|
| Cashless claim | Fill bank details section |
| Non-cashless | Leave bank details blank |
| All Yes/No fields | Mark "No" with filled underline bar |
| AM/PM | Underline the selected one |
| Mobile number | Not filled (skipped in v1) |
| State | Always "Tamil Nadu" |
| Font size | 9pt for all text, 8pt for workshop address |
| Text alignment | Centered within each field area |
| Yes/No marking | Filled black rectangle under "No" text |

---

## 8. Output

- Single-page filled PDF
- Same dimensions as blank form (595.56 × 842.04 pts / A4)
- Print-ready (text embedded, not annotations)
- Download filename: `claim_<reg_no>.pdf`

---

## 9. Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| Platform | Mobile browser (Android/iOS) |
| Network | Internet required (Claude API call) |
| Response time | < 20 seconds end-to-end |
| Input file size | Up to ~5MB combined PDF |
| Offline capability | Partial — PDF generation is client-side |
| API key security | Stored in browser localStorage |
| Data privacy | No data stored on any server |

---

## 10. What is NOT Automated

- Signature of insured (must be signed physically after printing)
- Claim number (assigned by insurer, not prefilled)
- Satisfaction note / additional documents
- Email field in workshop section

---

## 11. Known Limitations (v1)

- Only Dharmapuri branch form supported
- Only United India Insurance claim form
- Claude extraction accuracy depends on scan quality of uploaded documents
- Coordinates are hardcoded — any form layout change requires code update
- No field validation or preview before download
- API key visible to anyone with phone access
