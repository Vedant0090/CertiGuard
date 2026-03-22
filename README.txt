# 🛡️ CertiGuard — Academia Authenticity Validator

<div align="center">

![CertiGuard Banner](https://img.shields.io/badge/CertiGuard-MVP%20v1.0-00e5a0?style=for-the-badge&logo=shield&logoColor=black)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.9-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**A dual-tier certificate verification system using AI forensic analysis and cryptographic hashing.**  
Built for Smart India Hackathon 2025 · Team Hack4Good

[Features](#-features) · [Tech Stack](#-tech-stack) · [Installation](#-installation) · [Usage](#-usage) · [API](#-api-reference) · [Project Structure](#-project-structure)

</div>

---

## 🚨 The Problem

Fake academic certificates are a growing crisis in India and worldwide:
- Employers cannot reliably verify certificates from thousands of institutions
- Manual verification is slow, expensive, and error-prone
- Existing solutions require expensive institutional partnerships
- Legacy certificates (pre-digital) have no verification mechanism at all

## ✅ Our Solution

CertiGuard provides **two independent verification tiers** that work together:

| Tier | Method | Best For |
|------|--------|----------|
| **Tier 1** | SHA-256 cryptographic hash + database lookup | New digitally issued certificates |
| **Tier 2** | AI forensic analysis (OCR + Computer Vision) | Legacy / physical scanned certificates |

---

## ✨ Features

### 🔐 Tier 1 — Hash Verification
- Computes **SHA-256 fingerprint** of any uploaded certificate file
- Even a **single pixel change** produces a completely different hash, instantly detecting tampering
- Checks hash against a local certificate database (upgradeable to real blockchain)
- Returns instant authentic / not-found result

### 🔬 Tier 2 — AI Forensic Analysis
- **Tesseract OCR** extracts all text from certificate images
- Checks for **30+ certificate keywords** (certify, awarded, degree, examination…)
- Matches against **known Indian institution database** (IITs, NITs, central universities, boards)
- **OpenCV Hough Circle Transform** detects circular seals and stamps
- **Signature region detection** in the lower half of the document
- **Noise pattern analysis** across image grid to detect copy-paste tampering
- **Border frame detection** — most real certificates have decorative borders
- Returns a **confidence score** (0–99%) with detailed per-check breakdown

### 🖥️ Frontend
- Clean dark-theme UI with drag-and-drop upload
- Live backend connection status indicator
- Animated step-by-step verification progress
- **Verify tab** — upload and verify any certificate
- **Register tab** — register new certificates into the database
- **How it works tab** — explainer for judges / users
- Download verification report as `.txt`
- Flag suspicious certificates for manual review

---

## 🛠 Tech Stack

**Backend**
- Python 3.10+
- Flask 3.0 — web server framework
- Flask-CORS — cross-origin request handling
- PyPDF2 — PDF text extraction
- Pillow — image reading and processing
- Tesseract OCR + pytesseract — text extraction from images
- OpenCV (cv2) — seal detection, noise analysis, image forensics
- NumPy — image array mathematics
- hashlib — SHA-256 hashing (built into Python)

**Frontend**
- Pure HTML5 / CSS3 / JavaScript (no framework needed)
- Google Fonts: Syne, DM Sans, DM Mono
- Runs directly in any browser — no build step

**Storage**
- `blockchain_db.json` — local JSON database for certificate hashes
- Upgradeable to Polygon blockchain (see Phase 4 notes)

---

## 📁 Project Structure

```
certiguard/
│
├── app.py                  # Flask web server — all API endpoints
├── verifier.py             # Main verification pipeline (calls all modules)
├── ocr_analysis.py         # Tesseract OCR + keyword/institution checks
├── image_forensics.py      # OpenCV seal, signature, tampering detection
├── register.py             # CLI tool to register certificates
│
├── certiguard.html         # Complete frontend (single file, no build needed)
│
├── requirements.txt        # Python dependencies
├── blockchain_db.json      # Auto-created — stores certificate hashes
├── uploads/                # Auto-created — temporary file storage
│
├── CertiGuard.sol          # Solidity smart contract (Phase 4 / optional)
├── blockchain.py           # Polygon blockchain connector (Phase 4 / optional)
├── qr_generator.py         # QR code + PDF certificate generator (Phase 4 / optional)
│
└── README.md
```

---

## ⚙️ Installation

### Prerequisites
- Python 3.10 or newer — [python.org](https://python.org/downloads)
- Tesseract OCR engine — [installation guide below](#tesseract-installation)

### Step 1 — Clone the repository
```bash
git clone https://github.com/yourusername/certiguard.git
cd certiguard
```

### Step 2 — Install Python dependencies
```bash
pip install -r requirements.txt
```

This installs: Flask, Flask-CORS, PyPDF2, Pillow, pytesseract, opencv-python, numpy

### Step 3 — Install Tesseract OCR engine

**Windows:**
1. Download the installer from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run `tesseract-ocr-w64-setup-5.x.x.exe` with default settings
3. Note the install path (usually `C:\Program Files\Tesseract-OCR\`)
4. The path is already configured in `app.py` — update if yours is different:
```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

**Linux/Mac:**
```bash
# Ubuntu/Debian
sudo apt install tesseract-ocr

# macOS
brew install tesseract
```
On Linux/Mac, remove the `tesseract_cmd` line from `app.py` — it's not needed.

### Step 4 — Start the backend server
```bash
python app.py
```

You should see:
```
==================================================
  CertiGuard Backend - Phase 3
  Running at: http://localhost:5000
  OCR + Image Forensics: ACTIVE
  Press CTRL+C to stop
==================================================
```

### Step 5 — Open the frontend
Open `certiguard.html` in any browser.  
The green dot in the top-right confirms the backend is connected.

---

## 🚀 Usage

### Verifying a Certificate

1. Open `certiguard.html` in your browser
2. Drag and drop a certificate file (PDF, PNG, or JPG)
3. Select your verification mode:
   - **Tier 1** — for certificates registered in the database
   - **Tier 2** — for legacy or unregistered certificates (full AI analysis)
4. Click **Verify Certificate**
5. View the result: verdict, confidence score, and detailed per-check breakdown

### Registering a Certificate

1. Click the **Register** tab
2. Fill in student name, course, institution
3. Upload the certificate file
4. Click **Register Certificate**
5. The SHA-256 hash is stored in `blockchain_db.json`
6. Now uploading that same file in the Verify tab will return **Authentic**

### CLI Registration (alternative)
```bash
# Register a certificate
python register.py path/to/certificate.pdf

# List all registered certificates
python register.py --list
```

---

## 📡 API Reference

Base URL: `http://localhost:5000`

### `GET /health`
Health check — confirms server is running.
```json
{ "status": "ok", "phase": "3" }
```

### `POST /verify`
Verify a certificate file.

**Request:** `multipart/form-data`
| Field | Type | Description |
|-------|------|-------------|
| `file` | File | Certificate (PDF/PNG/JPG, max 10MB) |
| `mode` | String | `"1"` = Hash check, `"2"` = AI Forensic |

**Response:**
```json
{
  "verdict": "Authentic",
  "confidence": 87,
  "hash": "a3f1c2d4...",
  "blockchain_found": false,
  "mode": "AI Forensic",
  "file_type": "PNG",
  "message": "Certificate verified successfully.",
  "extracted_text_preview": "CERTIFICATE OF COMPLETION...",
  "checks": [
    { "name": "OCR text extraction", "detail": "Found 142 words", "status": "pass" },
    { "name": "Seal / stamp", "detail": "1 circular seal detected", "status": "pass" }
  ],
  "timestamp": "2026-03-22T12:00:00"
}
```

### `POST /register`
Register a certificate hash.

**Request:** `multipart/form-data`
| Field | Type | Description |
|-------|------|-------------|
| `file` | File | Certificate file to register |
| `student_name` | String | Student's full name |
| `course_name` | String | Course or degree name |
| `institution` | String | Issuing institution |

**Response:**
```json
{
  "success": true,
  "file_hash": "a3f1c2d4...",
  "tx_hash": "local_abc123",
  "message": "Registered in local database"
}
```

---

## 🔍 Verification Checks Explained

| Check | What it does | Pass condition |
|-------|-------------|----------------|
| **Blockchain hash** | Looks up SHA-256 in database | Hash found in `blockchain_db.json` |
| **File size** | Checks file size is in normal range | Between 15 KB and 9 MB |
| **Image resolution** | Checks pixel dimensions | Width ≥ 1200px, height ≥ 800px |
| **OCR extraction** | Reads all text via Tesseract | More than 10 words extracted |
| **Certificate keywords** | Scans for 30+ known keywords | 5 or more keywords found |
| **Institution check** | Matches known Indian institutions | Name found in database |
| **Date field** | Looks for dates/years in text | Date pattern found |
| **Suspicious content** | Checks for "sample", "void", "template" etc. | No suspicious phrases found |
| **Seal / stamp** | OpenCV circle detection | ≥1 circular region detected |
| **Signature region** | Horizontal dark strokes in lower half | Signature-like contours found |
| **Border / frame** | Edge pixels darker than centre | Border present |
| **Tampering check** | Noise consistency across 4×4 grid | Noise variation score < 25 |

---

## 🗺️ Roadmap

- [x] **Phase 1** — Frontend UI (dark theme, drag-and-drop, animated results)
- [x] **Phase 2** — Python backend (Flask server, SHA-256 hashing, local database)
- [x] **Phase 3** — AI analysis (Tesseract OCR, OpenCV forensics, confidence scoring)
- [ ] **Phase 4** — Real blockchain (Polygon Amoy testnet, smart contract, QR code generation)
- [ ] **Phase 5** — Admin dashboard, bulk verification, institution portal
- [ ] **Phase 6** — Mobile app (React Native)

---

## 🤝 Contributing

Pull requests are welcome!

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---


## 🙏 Acknowledgements

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) — Google's open-source OCR engine
- [OpenCV](https://opencv.org/) — Open source computer vision library
- [Flask](https://flask.palletsprojects.com/) — Lightweight Python web framework
- [Polygon](https://polygon.technology/) — Ethereum scaling blockchain (Phase 4)

---

<div align="center">
  <strong>Built with ❤️ for Smart India Hackathon 2025</strong><br/>
  <sub>CertiGuard — Making fake certificates a thing of the past</sub>
</div>
