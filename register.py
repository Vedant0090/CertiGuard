# ============================================================
# CertiGuard — Certificate Registration Tool
# register.py  ·  Add certificates to the blockchain database
# ============================================================
# Use this when a university ISSUES a certificate.
# Run it like this:
#   python register.py path/to/certificate.pdf
# ============================================================

import sys
import json
import os
import datetime
import hashlib

DB_FILE = "blockchain_db.json"

def compute_hash(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)

def register(filepath):
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return

    print(f"\n📄 Registering: {filepath}")
    file_hash = compute_hash(filepath)
    print(f"🔑 SHA-256 Hash: {file_hash}")

    db = load_db()

    if file_hash in db:
        print(f"ℹ️  Already registered on: {db[file_hash]['registered_at'][:10]}")
        return

    db[file_hash] = {
        "filename": os.path.basename(filepath),
        "registered_at": datetime.datetime.now().isoformat(),
        "status": "valid"
    }
    save_db(db)
    print(f"✅ Registered successfully!")
    print(f"📦 Total certificates in DB: {len(db)}")

def list_all():
    db = load_db()
    if not db:
        print("📭 No certificates registered yet.")
        return
    print(f"\n📋 Registered Certificates ({len(db)} total):\n")
    for h, record in db.items():
        print(f"  Hash   : {h[:20]}...")
        print(f"  File   : {record['filename']}")
        print(f"  Date   : {record['registered_at'][:10]}")
        print(f"  Status : {record['status']}")
        print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python register.py <filepath>    — register a certificate")
        print("  python register.py --list        — show all registered certs")
        sys.exit(1)

    if sys.argv[1] == "--list":
        list_all()
    else:
        register(sys.argv[1])
