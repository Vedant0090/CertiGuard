# ============================================================
# CertiGuard — Phase 3 · OCR Analysis
# ocr_analysis.py  ·  Extract and verify text from certificates
# ============================================================
# What this file does:
#   - Uses pytesseract (Tesseract OCR) to read text from images
#   - Falls back to PyPDF2 for PDF files
#   - Checks for expected certificate fields (name, date, institute)
#   - Returns extracted text + a list of check results
# ============================================================

import re

# ── Try importing OCR libraries ───────────────────────────
try:
    import pytesseract          # the OCR engine
    from PIL import Image       # opens image files
    OCR_SUPPORT = True
except ImportError:
    OCR_SUPPORT = False

try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False


# ── Known Indian universities / boards (expandable list) ──
KNOWN_INSTITUTIONS = [
    # Central universities
    "university of delhi", "jawaharlal nehru university", "banaras hindu university",
    "aligarh muslim university", "hyderabad university", "jamia millia",
    # IITs
    "iit bombay", "iit delhi", "iit madras", "iit kanpur", "iit kharagpur",
    "iit roorkee", "iit guwahati", "indian institute of technology",
    # NITs
    "national institute of technology", "nit trichy", "nit warangal",
    # Boards
    "cbse", "central board of secondary education",
    "icse", "council for the indian school certificate",
    "state board", "maharashtra board", "up board", "rajasthan board",
    # Common suffixes
    "college of engineering", "institute of technology", "deemed university",
    "autonomous college",
]

# Words that should appear in a real certificate
CERTIFICATE_KEYWORDS = [
    "certificate", "certify", "certifies", "awarded", "conferred",
    "completed", "successfully", "achieved", "degree", "diploma",
    "bachelor", "master", "doctor", "ph.d", "b.tech", "m.tech",
    "b.sc", "m.sc", "b.com", "m.com", "b.a", "m.a",
    "examination", "course", "program", "programme",
    "grade", "marks", "percentage", "cgpa", "gpa",
    "principal", "director", "registrar", "chairman",
    "university", "institute", "college", "school", "board",
    "dated", "date", "year", "session",
]

# Red-flag words that suggest tampering or fakery
SUSPICIOUS_PHRASES = [
    "photoshop", "edited", "template", "sample", "specimen",
    "watermark", "draft", "copy", "duplicate", "void",
    "not valid", "invalid", "test certificate", "demo",
]


def extract_text_from_image(filepath):
    """
    Use Tesseract OCR to extract text from a PNG/JPG image.
    Returns the extracted text string, or None if OCR not available.
    """
    if not OCR_SUPPORT:
        return None, "pytesseract not installed"

    try:
        img = Image.open(filepath)

        # Convert to RGB if needed (OCR works best on RGB)
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")

        # Run OCR — config: treat as single page of text
        text = pytesseract.image_to_string(img, config="--psm 1")
        return text.strip(), None

    except pytesseract.TesseractNotFoundError:
        return None, "Tesseract engine not installed — see README for setup"
    except Exception as e:
        return None, str(e)


def extract_text_from_pdf(filepath):
    """
    Extract text from a PDF using PyPDF2.
    Returns (text, error_message).
    """
    if not PDF_SUPPORT:
        return None, "PyPDF2 not installed"

    try:
        text = ""
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
        return text.strip(), None
    except Exception as e:
        return None, str(e)


def analyze_ocr(filepath):
    """
    Main OCR analysis function.
    Extracts text and runs multiple checks on it.

    Returns:
      checks (list): list of check result dicts
      confidence_delta (int): how much to adjust the confidence score
      extracted_text (str): the raw text found (for other modules to use)
    """
    checks = []
    confidence_delta = 0
    ext = filepath.rsplit(".", 1)[-1].lower()

    # ── Step 1: Extract text ──────────────────────────────
    if ext == "pdf":
        text, error = extract_text_from_pdf(filepath)
        method = "PyPDF2"
    else:
        text, error = extract_text_from_image(filepath)
        method = "Tesseract OCR"

    if error and not text:
        checks.append({
            "name": "OCR text extraction",
            "detail": f"Could not extract text: {error}",
            "status": "warn"
        })
        return checks, 0, ""

    if not text or len(text) < 10:
        checks.append({
            "name": "OCR text extraction",
            "detail": "Very little text found — may be a blank or image-only file",
            "status": "warn"
        })
        return checks, -10, ""

    char_count = len(text)
    word_count = len(text.split())

    checks.append({
        "name": "OCR text extraction",
        "detail": f"{method} found {word_count} words ({char_count} characters)",
        "status": "pass"
    })
    confidence_delta += 10

    # ── Step 2: Certificate keyword check ────────────────
    text_lower = text.lower()
    found_keywords = [kw for kw in CERTIFICATE_KEYWORDS if kw in text_lower]

    if len(found_keywords) >= 5:
        checks.append({
            "name": "Certificate keywords",
            "detail": f"Found {len(found_keywords)} keywords: {', '.join(found_keywords[:5])}…",
            "status": "pass"
        })
        confidence_delta += 15
    elif len(found_keywords) >= 2:
        checks.append({
            "name": "Certificate keywords",
            "detail": f"Only {len(found_keywords)} keywords found — borderline",
            "status": "warn"
        })
        confidence_delta += 5
    else:
        checks.append({
            "name": "Certificate keywords",
            "detail": "Very few certificate keywords — suspicious",
            "status": "fail"
        })
        confidence_delta -= 20

    # ── Step 3: Institution name check ───────────────────
    found_institutions = [inst for inst in KNOWN_INSTITUTIONS if inst in text_lower]

    if found_institutions:
        checks.append({
            "name": "Institution check",
            "detail": f"Recognised: {found_institutions[0].title()}",
            "status": "pass"
        })
        confidence_delta += 10
    else:
        # Check for generic institution indicators
        generic = any(w in text_lower for w in ["university", "college", "institute", "board", "school"])
        if generic:
            checks.append({
                "name": "Institution check",
                "detail": "Institution mentioned but not in known database",
                "status": "warn"
            })
        else:
            checks.append({
                "name": "Institution check",
                "detail": "No institution name detected",
                "status": "fail"
            })
            confidence_delta -= 10

    # ── Step 4: Date / year check ────────────────────────
    # Look for patterns like: 12/03/2023, 2023, March 2023, 12-03-2023
    date_patterns = [
        r"\b(19|20)\d{2}\b",                          # year: 1900–2099
        r"\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b",   # DD/MM/YYYY
        r"\b(january|february|march|april|may|june|july|august|"
        r"september|october|november|december)\b",      # month name
    ]
    date_found = any(re.search(p, text_lower) for p in date_patterns)

    if date_found:
        checks.append({
            "name": "Date field",
            "detail": "Date or year found in document",
            "status": "pass"
        })
        confidence_delta += 5
    else:
        checks.append({
            "name": "Date field",
            "detail": "No date found — unusual for a certificate",
            "status": "warn"
        })
        confidence_delta -= 5

    # ── Step 5: Suspicious phrase check ──────────────────
    found_suspicious = [p for p in SUSPICIOUS_PHRASES if p in text_lower]

    if found_suspicious:
        checks.append({
            "name": "Suspicious content",
            "detail": f"Found suspicious words: {', '.join(found_suspicious)}",
            "status": "fail"
        })
        confidence_delta -= 30
    else:
        checks.append({
            "name": "Suspicious content",
            "detail": "No suspicious phrases detected",
            "status": "pass"
        })
        confidence_delta += 5

    return checks, confidence_delta, text
