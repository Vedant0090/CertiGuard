# ============================================================
# CertiGuard — Verifier (Render-safe version)
# verifier.py
# ============================================================

import hashlib
import os
import json
import datetime

# ── Safe imports — won't crash if libraries missing ───────
try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

try:
    from PIL import Image
    IMAGE_SUPPORT = True
except ImportError:
    IMAGE_SUPPORT = False

try:
    import pytesseract
    OCR_SUPPORT = True
except ImportError:
    OCR_SUPPORT = False

try:
    import cv2
    import numpy as np
    CV_SUPPORT = True
except ImportError:
    CV_SUPPORT = False


# ── Database ──────────────────────────────────────────────
DB_FILE = "blockchain_db.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}


# ── Hash ──────────────────────────────────────────────────
def compute_hash(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()


# ── OCR ───────────────────────────────────────────────────
def run_ocr(filepath):
    ext = filepath.rsplit(".", 1)[-1].lower()
    text = ""

    if ext == "pdf" and PDF_SUPPORT:
        try:
            with open(filepath, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() or ""
        except Exception:
            pass
    elif ext in ("png", "jpg", "jpeg") and OCR_SUPPORT and IMAGE_SUPPORT:
        try:
            img = Image.open(filepath)
            text = pytesseract.image_to_string(img)
        except Exception:
            pass

    return text.strip()


# ── Keyword check ─────────────────────────────────────────
KEYWORDS = [
    "certificate", "certify", "certifies", "awarded", "conferred",
    "completed", "successfully", "degree", "diploma", "bachelor",
    "master", "b.tech", "m.tech", "examination", "university",
    "institute", "college", "board", "principal", "registrar"
]

SUSPICIOUS = ["sample", "void", "template", "draft", "specimen", "demo"]


# ── Image checks ──────────────────────────────────────────
def run_image_checks(filepath):
    checks = []
    delta = 0
    ext = filepath.rsplit(".", 1)[-1].lower()

    if ext not in ("png", "jpg", "jpeg"):
        return checks, delta

    if IMAGE_SUPPORT:
        try:
            img = Image.open(filepath)
            w, h = img.size
            if w >= 1200 and h >= 800:
                checks.append({"name": "Image resolution", "detail": f"{w}x{h}px — high quality", "status": "pass"})
                delta += 10
            elif w >= 600:
                checks.append({"name": "Image resolution", "detail": f"{w}x{h}px — medium quality", "status": "warn"})
                delta += 3
            else:
                checks.append({"name": "Image resolution", "detail": f"{w}x{h}px — low resolution", "status": "fail"})
                delta -= 10
        except Exception:
            pass

    if CV_SUPPORT:
        try:
            img_cv = cv2.imread(filepath)
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            h, w = gray.shape

            # Seal detection
            blurred = cv2.GaussianBlur(gray, (9, 9), 2)
            circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, 1.2, 50,
                                        param1=80, param2=30,
                                        minRadius=w//30, maxRadius=w//4)
            if circles is not None:
                checks.append({"name": "Seal / stamp", "detail": f"{len(circles[0])} circular seal(s) detected", "status": "pass"})
                delta += 15
            else:
                checks.append({"name": "Seal / stamp", "detail": "No circular seal detected", "status": "warn"})
                delta -= 5

            # Noise / tampering
            grid_stds = []
            gh, gw = h // 4, w // 4
            for r in range(4):
                for c in range(4):
                    cell = gray[r*gh:(r+1)*gh, c*gw:(c+1)*gw]
                    grid_stds.append(float(np.std(cell)))
            noise_var = float(np.std(grid_stds))
            if noise_var > 25:
                checks.append({"name": "Tampering check", "detail": f"Inconsistent noise detected (score: {noise_var:.1f})", "status": "fail"})
                delta -= 20
            else:
                checks.append({"name": "Tampering check", "detail": f"Noise pattern consistent (score: {noise_var:.1f})", "status": "pass"})
                delta += 10

        except Exception:
            pass

    return checks, delta


# ── MAIN ─────────────────────────────────────────────────
def verify_certificate(filepath, mode="1"):
    ext = filepath.rsplit(".", 1)[-1].lower()
    all_checks = []
    confidence = 50

    # Step 1 — Hash
    file_hash = compute_hash(filepath)
    db = load_db()
    blockchain_found = file_hash in db

    if blockchain_found:
        record = db[file_hash]
        all_checks.append({
            "name": "Blockchain hash",
            "detail": f"Hash found — registered {record.get('registered_at','')[:10]}",
            "status": "pass"
        })
        confidence += 30
    else:
        all_checks.append({
            "name": "Blockchain hash",
            "detail": "Hash not found in database",
            "status": "fail" if mode == "1" else "warn"
        })
        if mode == "1":
            confidence -= 20

    # Step 2 — File size
    size_kb = os.path.getsize(filepath) / 1024
    if 15 < size_kb < 9000:
        all_checks.append({"name": "File size", "detail": f"{size_kb:.1f} KB — normal", "status": "pass"})
        confidence += 5
    else:
        all_checks.append({"name": "File size", "detail": f"{size_kb:.1f} KB — unusual", "status": "warn"})

    # Step 3 — OCR
    text = run_ocr(filepath)
    if text and len(text) > 20:
        all_checks.append({
            "name": "OCR text extraction",
            "detail": f"Extracted {len(text.split())} words",
            "status": "pass"
        })
        confidence += 10

        text_lower = text.lower()
        found_kw = [k for k in KEYWORDS if k in text_lower]
        if len(found_kw) >= 5:
            all_checks.append({"name": "Certificate keywords", "detail": f"Found: {', '.join(found_kw[:4])}…", "status": "pass"})
            confidence += 15
        elif len(found_kw) >= 2:
            all_checks.append({"name": "Certificate keywords", "detail": f"Only {len(found_kw)} keywords found", "status": "warn"})
            confidence += 5
        else:
            all_checks.append({"name": "Certificate keywords", "detail": "Very few keywords detected", "status": "fail"})
            confidence -= 15

        found_sus = [s for s in SUSPICIOUS if s in text_lower]
        if found_sus:
            all_checks.append({"name": "Suspicious content", "detail": f"Found: {', '.join(found_sus)}", "status": "fail"})
            confidence -= 25
        else:
            all_checks.append({"name": "Suspicious content", "detail": "No suspicious phrases found", "status": "pass"})
            confidence += 5
    else:
        all_checks.append({
            "name": "OCR text extraction",
            "detail": "Tesseract not available on server — install via system packages" if not OCR_SUPPORT else "Little text found",
            "status": "warn"
        })

    # Step 4 — Image forensics
    img_checks, img_delta = run_image_checks(filepath)
    all_checks.extend(img_checks)
    confidence += img_delta

    # Step 5 — Clamp + verdict
    confidence = max(5, min(99, confidence))

    if blockchain_found:
        verdict = "Authentic"
    elif confidence >= 72:
        verdict = "Authentic"
    elif confidence >= 45:
        verdict = "Suspicious"
    else:
        verdict = "Fraudulent"

    messages = {
        "Authentic":  "Certificate verified successfully — no tampering detected.",
        "Suspicious": "Anomalies detected — flagged for manual review.",
        "Fraudulent": "Certificate appears to be fabricated — do not accept."
    }

    return {
        "verdict": verdict,
        "confidence": confidence,
        "hash": file_hash,
        "blockchain_found": blockchain_found,
        "mode": "Blockchain" if mode == "1" else "AI Forensic",
        "file_type": ext.upper(),
        "checks": all_checks,
        "extracted_text_preview": text[:300] if text else "",
        "timestamp": datetime.datetime.now().isoformat(),
        "message": messages[verdict],
        "phase": "3"
    }