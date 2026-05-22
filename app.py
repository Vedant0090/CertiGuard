# ============================================================
# CertiGuard — Production Backend (Render deployment)
# app.py
# ============================================================

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import hashlib
import json
import datetime

from verifier import verify_certificate

app = Flask(__name__)

# ── Allow ALL origins (fixes CORS for GitHub Pages) ──────
CORS(app, origins="*", supports_credentials=False)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ── CORS preflight handler (OPTIONS requests) ─────────────
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"]  = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "running",
        "message": "CertiGuard backend is live!",
        "version": "1.0.0",
        "phase": "3"
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "phase": "3"})


@app.route("/verify", methods=["POST", "OPTIONS"])
def verify():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    mode = request.form.get("mode", "1")

    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Use PDF, PNG or JPG."}), 400

    # Save with safe filename
    safe_name = hashlib.md5(file.filename.encode()).hexdigest()[:12] + \
                "." + file.filename.rsplit(".", 1)[-1].lower()
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], safe_name)
    file.save(filepath)

    try:
        result = verify_certificate(filepath, mode)
        os.remove(filepath)
        return jsonify(result)
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({"error": str(e)}), 500


@app.route("/register", methods=["POST", "OPTIONS"])
def register():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    DB_FILE = "blockchain_db.json"

    def load_db():
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r") as f:
                return json.load(f)
        return {}

    def save_db(db):
        with open(DB_FILE, "w") as f:
            json.dump(db, f, indent=2)

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    student_name = request.form.get("student_name", "Unknown")
    course_name  = request.form.get("course_name", "Unknown")
    institution  = request.form.get("institution", "Unknown")

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    safe_name = hashlib.md5(file.filename.encode()).hexdigest()[:12] + \
                "." + file.filename.rsplit(".", 1)[-1].lower()
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], safe_name)
    file.save(filepath)

    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    file_hash = sha256.hexdigest()
    os.remove(filepath)

    db = load_db()
    db[file_hash] = {
        "student_name":  student_name,
        "course_name":   course_name,
        "institution":   institution,
        "registered_at": datetime.datetime.now().isoformat(),
        "filename":      file.filename
    }
    save_db(db)

    return jsonify({
        "success":   True,
        "file_hash": file_hash,
        "tx_hash":   "local_" + file_hash[:16],
        "message":   "Registered successfully"
    })


if __name__ == "__main__":
    print("\n" + "="*50)
    print("  CertiGuard Backend - Phase 3")
    print("  Running at: http://localhost:5000")
    print("  Press CTRL+C to stop")
    print("="*50 + "\n")
    app.run(debug=True, port=5000)