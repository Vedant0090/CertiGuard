# ============================================================
# CertiGuard — Phase 3 Backend Server
# app.py  ·  Main Flask application
# ============================================================

from flask import Flask, request, jsonify
from flask_cors import CORS
import os

# ── Tesseract OCR path (Windows) ─────────────────────────
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

from verifier import verify_certificate

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def home():
    return jsonify({
        "status": "running",
        "message": "CertiGuard backend is live!",
        "version": "0.3.0",
        "endpoints": ["/verify", "/health"]
    })


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/verify", methods=["POST"])
def verify():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    mode = request.form.get("mode", "1")

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed. Use PDF, PNG, or JPG."}), 400

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    try:
        result = verify_certificate(filepath, mode)
        os.remove(filepath)
        return jsonify(result)

    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("\n" + "="*50)
    print("  CertiGuard Backend - Phase 3")
    print("  Running at: http://localhost:5000")
    print("  OCR + Image Forensics: ACTIVE")
    print("  Press CTRL+C to stop")
    print("="*50 + "\n")
    app.run(debug=True, port=5000)
