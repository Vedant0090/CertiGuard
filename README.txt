# CertiGuard — AI-Powered Certificate Verification System

A modern certificate verification and fraud detection platform that helps organizations validate digital certificates securely using AI-assisted verification workflows and automated validation pipelines.

---

## 🚀 Features

* 🔍 AI-powered certificate validation
* 📄 Upload and verify certificates instantly
* 🛡️ Fraud & tampering detection
* 📊 Admin dashboard for certificate management
* ⚡ Real-time verification status
* 🔐 Secure authentication & authorization
* ☁️ Cloud deployment ready
* 📱 Responsive modern UI

---

## 🧠 Problem Statement

Fake and tampered certificates are becoming increasingly common in:

* hiring processes
* online certifications
* academic institutions
* training programs

Manual verification is:

* slow
* error-prone
* difficult to scale

**CertiGuard** automates the verification workflow and helps organizations detect suspicious or invalid certificates efficiently.

---

## 🛠️ Tech Stack

### Frontend

* React.js / Next.js
* Tailwind CSS
* TypeScript

### Backend

* Node.js / Express.js
* FastAPI (if AI module separated)

### Database

* PostgreSQL / MongoDB

### AI & OCR

* OpenAI API
* OCR-based text extraction

### Authentication

* JWT Authentication

### Deployment

* Vercel
* Render / Railway

---

## ⚙️ System Workflow

```text
Certificate Upload
        ↓
OCR/Text Extraction
        ↓
AI Verification Engine
        ↓
Fraud Detection & Validation
        ↓
Verification Result
        ↓
Dashboard Storage
```

---

## 📂 Project Structure

```bash
CertiGuard/
│
├── frontend/
│   ├── components/
│   ├── pages/
│   ├── services/
│   └── utils/
│
├── backend/
│   ├── routes/
│   ├── controllers/
│   ├── models/
│   ├── middleware/
│   └── services/
│
├── database/
├── docs/
└── README.md
```

---

## 🔑 Core Functionalities

### 1. Certificate Upload

Users can upload certificates in:

* PDF
* PNG
* JPG

---

### 2. OCR Extraction

The system extracts:

* candidate name
* issuer name
* issue date
* certificate ID

---

### 3. AI Verification

AI analyzes:

* formatting consistency
* suspicious modifications
* metadata anomalies
* issuer validation

---

### 4. Verification Result

Returns:

* Verified ✅
* Suspicious ⚠️
* Invalid ❌

---

## 🗄️ Database Schema

### certificates

```sql
CREATE TABLE certificates (
    id UUID PRIMARY KEY,
    candidate_name TEXT,
    issuer_name TEXT,
    certificate_id TEXT,
    issue_date DATE,
    verification_status TEXT,
    ai_confidence_score FLOAT,
    uploaded_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔐 Environment Variables

### Backend

```env
OPENAI_API_KEY=
DATABASE_URL=
JWT_SECRET=
```

### Frontend

```env
NEXT_PUBLIC_API_URL=
```

---

## 🧪 Installation

### Clone Repository

```bash
git clone https://github.com/Vedant0090/CertiGuard.git
cd CertiGuard
```

---

## Install Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Install Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## 🌐 Deployment

### Frontend

Deploy on:

* [Vercel](https://vercel.com?utm_source=chatgpt.com)

### Backend

Deploy on:

* [Render](https://render.com?utm_source=chatgpt.com)
* [Railway](https://railway.app?utm_source=chatgpt.com)

### Database

Use:

* [Supabase](https://supabase.com?utm_source=chatgpt.com)
* [Neon](https://neon.tech?utm_source=chatgpt.com)

---

## 📸 Screenshots

Add screenshots here:

```md
![Dashboard Screenshot](./screenshots/dashboard.png)
```

---

## 🎯 Future Improvements

* Blockchain-backed certificate validation
* QR-based instant verification
* Multi-language OCR
* Bulk certificate processing
* AI anomaly scoring
* Email verification workflows

---

## 💼 Business Use Cases

* Educational Institutions
* HR & Recruitment Platforms
* Online Certification Providers
* Corporate Training Programs

---

## 🤝 Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Open a pull request

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

Vedant Srivastava

* [GitHub Profile](https://github.com/Vedant0090?utm_source=chatgpt.com)
* [LinkedIn](https://www.linkedin.com?utm_source=chatgpt.com)

---

## ⭐ Support

If you found this project useful, consider giving it a star on GitHub ⭐
