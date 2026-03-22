# 🛡️ CertiGuard — Academia Authenticity Validator


## 🚨 The Problem

Fake academic certificates are a serious and growing problem across India:

- Thousands of fraudulent degrees and diplomas enter the job market every year
- Employers have no fast, reliable way to verify certificates from hundreds of institutions
- Manual verification takes days, costs money, and is still often inaccurate
- Physical and scanned legacy certificates have no digital verification mechanism at all

The result — unqualified candidates get jobs they don't deserve, and honest students lose out.

---

## ✅ The Solution

CertiGuard is a dual-tier certificate verification system that gives an instant, AI-powered verdict on whether any certificate is authentic, suspicious, or fraudulent.

**Tier 1 — Cryptographic Hash Verification**

Every legitimate certificate has a unique SHA-256 fingerprint stored in the database at the time of issue. When someone uploads a certificate to verify it, CertiGuard computes the fingerprint of the uploaded file and compares it with the database. Even changing a single pixel produces a completely different fingerprint — making tampering instantly detectable.

**Tier 2 — AI Forensic Analysis**

For legacy certificates that predate digital issuance, CertiGuard runs a full AI forensic pipeline. Tesseract OCR reads all text from the document and checks it against 30+ certificate keywords and a database of known Indian institutions. OpenCV computer vision detects circular seals and stamps, finds signature regions, and analyses noise patterns across the image to catch copy-paste tampering. The result is a confidence score from 0–99% with a detailed breakdown of every check.

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Backend | Python 3.10, Flask | Web server and API |
| Hashing | hashlib (SHA-256) | Tamper-proof fingerprinting |
| OCR | Tesseract + pytesseract | Text extraction from images |
| Computer Vision | OpenCV, NumPy | Seal detection, tampering analysis |
| PDF Reading | PyPDF2 | Text extraction from PDF files |
| Image Processing | Pillow | Image loading and pre-processing |
| Frontend | HTML, CSS, JavaScript | Single-file UI, no framework needed |
| Storage | JSON flat file | Certificate hash database |
| Deployment | Render + GitHub Pages | Free hosting |

---

## ⚙️ How It Works

```
User uploads certificate (PDF / PNG / JPG)
          │
          ▼
   Compute SHA-256 hash
          │
          ├──► Hash found in DB ──────────────────► ✅ Authentic
          │
          └──► Hash not found → Run AI Forensic Analysis
                    │
                    ├── Tesseract OCR     → extract all text
                    ├── Keyword check     → certificate vocabulary
                    ├── Institution match → known Indian universities
                    ├── OpenCV            → detect circular seals
                    ├── Signature check   → lower-region stroke detection
                    ├── Noise analysis    → copy-paste artifact detection
                    └── Confidence score  → final verdict
```


## 🔍 AI Checks Explained

| Check | Tool | What It Detects |
|---|---|---|
| Text extraction | Tesseract OCR | All readable text in the document |
| Certificate keywords | String matching | Words like "certify", "awarded", "degree", "examination" |
| Institution match | Custom DB | Known IITs, NITs, central universities, state boards |
| Date detection | Regex | Presence of valid dates and years |
| Suspicious phrases | String matching | Words like "sample", "void", "template", "draft" |
| Seal detection | OpenCV Hough Circles | Circular stamps and official seals |
| Signature detection | OpenCV contours | Flowing dark strokes in the lower document area |
| Tampering check | NumPy noise analysis | Inconsistent noise patterns = copy-paste edits |
| Border detection | OpenCV pixel analysis | Decorative borders common on real certificates |
| Resolution check | Pillow | Low resolution is a red flag for screenshots |

---

## 📁 Project Structure

```
certiguard/
├── app.py               # Flask server — all API endpoints
├── verifier.py          # Main verification pipeline
├── ocr_analysis.py      # Tesseract OCR + keyword checks
├── image_forensics.py   # OpenCV seal, signature, tampering detection
├── register.py          # CLI tool to register certificates
├── certiguard.html      # Complete frontend (single HTML file)
├── requirements.txt     # Python dependencies
├── Procfile             # Render deployment config
└── runtime.txt          # Python version for Render
```

---

## 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/certiguard.git
cd certiguard

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the backend
python app.py

# 4. Open certiguard.html in your browser
```

> **Windows only:** Tesseract OCR must be installed separately.
> Download from: https://github.com/UB-Mannheim/tesseract/wiki

---

## 📄 License

MIT — free to use, modify and distribute.

---

<div align="center">
  <strong>Built for Smart India Hackathon 2025</strong><br/>
  <sub>Team Hack4Good · CertiGuard · Making fake certificates a thing of the past</sub>
</div>
