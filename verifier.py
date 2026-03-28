# ============================================================
# CertiGuard — Certificate Verification Logic (Phase 3)
# verifier.py  ·  Now with real OCR + image forensics
# ============================================================
# What's new in Phase 3:
#   - Real OCR text extraction (Tesseract for images, PyPDF2 for PDFs)
#   - Seal & stamp detection using OpenCV circle detection
#   - Signature region detection
#   - Noise/tampering artifact analysis
#   - Border frame detection
#   - Institution name matching
#   - Suspicious content phrase detection
# ============================================================

import hashlib
import os
import json
import datetime

# Phase 3 modules
from ocr_analysis import analyze_ocr
from image_forensics import analyze_image_forensics

# ── Try to import basic libraries ────────────────────────
try:
    from PIL import Image
    IMAGE_SUPPORT = True
except ImportError:
    IMAGE_SUPPORT = False

try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False


# ── Local "blockchain" database ───────────────────────────
DB_FILE = "blockchain_db.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)


# ── Core: Hash + Blockchain ───────────────────────────────

def compute_hash(filepath):
    """
    SHA-256 fingerprint of the file.
    Even a 1-pixel change produces a completely different hash.
    """
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()


def check_blockchain(file_hash):
    """Check local DB for this hash. Returns (found, record)."""
    db = load_db()
    if file_hash in db:
        return True, db[file_hash]
    return False, None


# ── Basic file checks (used for all file types) ───────────

def basic_file_checks(filepath):
    """
    Sanity checks that run on every file regardless of type.
    Returns (checks list, confidence_delta).
    """
    checks = []
    confidence_delta = 0
    ext = filepath.rsplit(".", 1)[-1].lower()
    size_bytes = os.path.getsize(filepath)
    size_kb = size_bytes / 1024

    # File size check
    if 15 < size_kb < 9000:
        checks.append({
            "name": "File size",
            "detail": f"{size_kb:.1f} KB — within normal range",
            "status": "pass"
        })
        confidence_delta += 5
    elif size_kb <= 15:
        checks.append({
            "name": "File size",
            "detail": f"{size_kb:.1f} KB — suspiciously small",
            "status": "fail"
        })
        confidence_delta -= 15
    else:
        checks.append({
            "name": "File size",
            "detail": f"{size_kb:.1f} KB — unusually large",
            "status": "warn"
        })

    # Image dimension check
    if ext in ("png", "jpg", "jpeg") and IMAGE_SUPPORT:
        try:
            img = Image.open(filepath)
            w, h = img.size
            if w >= 1200 and h >= 800:
                checks.append({
                    "name": "Image resolution",
                    "detail": f"{w}x{h}px — high quality",
                    "status": "pass"
                })
                confidence_delta += 10
            elif w >= 600:
                checks.append({
                    "name": "Image resolution",
                    "detail": f"{w}x{h}px — medium quality",
                    "status": "warn"
                })
                confidence_delta += 3
            else:
                checks.append({
                    "name": "Image resolution",
                    "detail": f"{w}x{h}px — too low for a real certificate",
                    "status": "fail"
                })
                confidence_delta -= 15
        except Exception:
            pass

    # PDF page count check
    if ext == "pdf" and PDF_SUPPORT:
        try:
            with open(filepath, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                pages = len(reader.pages)
            if pages == 1:
                checks.append({
                    "name": "PDF pages",
                    "detail": "Single-page PDF — typical for certificates",
                    "status": "pass"
                })
                confidence_delta += 5
            elif pages <= 4:
                checks.append({
                    "name": "PDF pages",
                    "detail": f"{pages} pages — acceptable",
                    "status": "warn"
                })
            else:
                checks.append({
                    "name": "PDF pages",
                    "detail": f"{pages} pages — unusual for a certificate",
                    "status": "warn"
                })
        except Exception:
            pass

    return checks, confidence_delta


# ── Verdict logic ─────────────────────────────────────────

def determine_verdict(confidence, blockchain_found):
    """Map confidence score to a verdict label."""
    if blockchain_found:
        return "Authentic", min(confidence, 99)
    if confidence >= 72:
        return "Authentic", confidence
    elif confidence >= 45:
        return "Suspicious", confidence
    else:
        return "Fraudulent", max(confidence, 5)


def get_verdict_message(verdict):
    return {
        "Authentic":  "Certificate verified successfully — no tampering detected.",
        "Suspicious": "Anomalies detected — flagged for manual review.",
        "Fraudulent": "Certificate appears to be fabricated — do not accept."
    }.get(verdict, "Verification complete.")


# ── MAIN FUNCTION ─────────────────────────────────────────

def verify_certificate(filepath, mode="1"):
    """
    Full verification pipeline.

    Mode 1 (Blockchain): Hash check is primary, forensics secondary.
    Mode 2 (AI Forensic): OCR + image forensics are primary.

    Returns a dict with everything the frontend needs.
    """

    ext = filepath.rsplit(".", 1)[-1].lower()
    all_checks = []
    total_confidence = 50   # neutral starting point

    # ════════════════════════════════════════════════════
    # STEP 1 — Compute SHA-256 hash
    # ════════════════════════════════════════════════════
    file_hash = compute_hash(filepath)

    # ════════════════════════════════════════════════════
    # STEP 2 — Blockchain / database check
    # ════════════════════════════════════════════════════
    blockchain_found, blockchain_record = check_blockchain(file_hash)

    if blockchain_found:
        reg_date = blockchain_record.get("registered_at", "")[:10]
        all_checks.append({
            "name": "Blockchain hash",
            "detail": f"Hash found — registered {reg_date}",
            "status": "pass"
        })
        total_confidence += 30
    else:
        all_checks.append({
            "name": "Blockchain hash",
            "detail": "Hash not in database — proceeding with AI analysis",
            "status": "fail" if mode == "1" else "warn"
        })
        if mode == "1":
            total_confidence -= 20

    # ════════════════════════════════════════════════════
    # STEP 3 — Basic file checks (size, resolution, pages)
    # ════════════════════════════════════════════════════
    basic_checks, basic_delta = basic_file_checks(filepath)
    all_checks.extend(basic_checks)
    total_confidence += basic_delta

    # ════════════════════════════════════════════════════
    # STEP 4 — OCR text analysis (Phase 3)
    # ════════════════════════════════════════════════════
    ocr_checks, ocr_delta, extracted_text = analyze_ocr(filepath)
    all_checks.extend(ocr_checks)
    total_confidence += ocr_delta

    # ════════════════════════════════════════════════════
    # STEP 5 — Image forensics: seal, signature, tampering
    #          (only for image files)
    # ════════════════════════════════════════════════════
    if ext in ("png", "jpg", "jpeg"):
        forensic_checks, forensic_delta = analyze_image_forensics(filepath)
        all_checks.extend(forensic_checks)
        multiplier = 1.0 if mode == "1" else 1.3
        total_confidence += int(forensic_delta * multiplier)
    else:
        all_checks.append({
            "name": "Image forensics",
            "detail": "Visual forensics available for PNG/JPG uploads",
            "status": "warn"
        })

    # ════════════════════════════════════════════════════
    # STEP 6 — Clamp confidence to 5-99
    # ════════════════════════════════════════════════════
    total_confidence = max(5, min(99, total_confidence))

    # ════════════════════════════════════════════════════
    # STEP 7 — Final verdict
    # ════════════════════════════════════════════════════
    verdict, final_confidence = determine_verdict(total_confidence, blockchain_found)

    return {
        "verdict": verdict,
        "confidence": final_confidence,
        "hash": file_hash,
        "blockchain_found": blockchain_found,
        "mode": "Blockchain" if mode == "1" else "AI Forensic",
        "file_type": ext.upper(),
        "checks": all_checks,
        "extracted_text_preview": extracted_text[:300] if extracted_text else "",
        "timestamp": datetime.datetime.now().isoformat(),
        "message": get_verdict_message(verdict),
        "phase": "3"
    }
