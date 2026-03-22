# CertiGuard — Phase 2 Setup Guide
========================================
HOW TO RUN THE BACKEND (step by step)
========================================

## YOUR FILES
  certiguard.html   ← open this in your browser (the UI)
  app.py            ← the web server (run this with Python)
  verifier.py       ← the analysis logic (app.py uses this)
  register.py       ← tool to add certificates to the database
  requirements.txt  ← list of Python packages to install

---

## STEP 1 — Install Python
  1. Go to https://python.org/downloads
  2. Download Python 3.10 or newer
  3. During install, CHECK the box "Add Python to PATH"
  4. Click Install

  To verify it worked, open a terminal and type:
    python --version
  You should see something like: Python 3.11.0

---

## STEP 2 — Open a Terminal in this folder
  Windows: Right-click in this folder → "Open in Terminal"
           OR press Windows+R, type cmd, press Enter, then type:
           cd path\to\this\folder

  Mac/Linux: Open Terminal, then type:
           cd path/to/this/folder

---

## STEP 3 — Install the required packages
  In your terminal, type exactly:
    pip install -r requirements.txt

  Wait for it to finish. You'll see packages being downloaded.

---

## STEP 4 — Start the backend server
  In your terminal, type:
    python app.py

  You should see:
    ==================================================
      CertiGuard Backend — Phase 2
      Running at: http://localhost:5000
      Press CTRL+C to stop
    ==================================================

  Leave this terminal window open! The server runs as long as this window is open.

---

## STEP 5 — Open the frontend
  Double-click certiguard.html to open it in your browser.
  The green dot in the top-right should say "backend online".

  Now upload any PDF or image and click "Verify Certificate"!

---

## BONUS — Register a certificate in the database
  To test the blockchain check, first register a file:
    python register.py path/to/certificate.pdf

  Then upload that same file in the browser — it will show "Authentic"
  because the hash matches the database.

  To see all registered certificates:
    python register.py --list

---

## TROUBLESHOOTING

  Problem: "python is not recognized"
  Fix: Re-install Python and make sure to check "Add to PATH"

  Problem: "No module named flask"
  Fix: Run: pip install -r requirements.txt

  Problem: Frontend shows "backend offline"
  Fix: Make sure you ran "python app.py" and the terminal is still open

  Problem: "Address already in use"
  Fix: Another program is using port 5000. Stop it, or change
       port=5000 to port=5001 in app.py AND change BACKEND_URL
       in certiguard.html to http://localhost:5001

---

## WHAT EACH FILE DOES (for your understanding)

  app.py        → Like a receptionist. Receives requests, passes
                  them to verifier.py, and sends back the answer.

  verifier.py   → The brain. Computes hash, checks database,
                  analyzes the file, calculates confidence score.

  register.py   → A helper tool to add certificates to the DB
                  (simulates a university issuing certificates).

  blockchain_db.json → Created automatically. Stores certificate
                        hashes. In Phase 4, this becomes a real
                        Polygon blockchain.

  certiguard.html → Your frontend from Phase 1, updated to call
                    the real backend instead of simulating.
