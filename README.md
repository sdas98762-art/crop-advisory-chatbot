# 🌾 Crop Advisory Chatbot

An AI-powered crop advisory web application that helps farmers get advice on **crop selection**, **disease diagnosis**, **weather-based guidance**, and **fertilizer/irrigation recommendations**.

> **Live Demo:** Run locally following the setup guide below.

---

## 🤖 AI Stack

| Component | Technology |
|---|---|
| **LLM (Chat)** | Google Gemini 3.6 Flash *(free tier)* |
| **Embeddings** | `all-MiniLM-L6-v2` *(runs locally, no API needed)* |
| **Vector Store** | ChromaDB *(local persistent)* |
| **Knowledge Base** | FAO & ICAR agriculture PDFs |
| **Weather** | OpenWeatherMap API *(free tier)* |

> ⚠️ This project uses **Google Gemini** — NOT OpenAI. Get your free Gemini API key at 👉 https://aistudio.google.com/app/apikey

---

## 🏗️ Architecture

```
React Frontend (http://localhost:5173)
        │
        ▼
FastAPI Backend (http://localhost:8000)
        │
        ├── RAG Pipeline (LangChain + ChromaDB + Gemini)
        ├── Disease Diagnosis (text symptoms + leaf image)
        ├── Weather Service (OpenWeatherMap)
        └── Intent Router (disease / weather / general)
```

---

## 📁 Project Structure

```
crop-advisory-chatbot/
├── frontend/               # React + Vite + TailwindCSS
│   └── src/
│       ├── api/            # Typed API client
│       ├── components/     # Chat UI, Weather Widget, Image Upload
│       └── types/
├── backend/                # Python + FastAPI
│   ├── api/                # Route handlers
│   ├── services/           # RAG, disease, weather, intent services
│   ├── ingestion/          # PDF → ChromaDB pipeline
│   │   └── sources/        # Place your agriculture PDFs here
│   ├── prompts/            # LLM prompt templates
│   ├── tests/              # pytest test suite
│   ├── config.py
│   ├── main.py
│   └── requirements.txt
├── .env.example            # Environment variable template
├── .gitignore
└── README.md
```

---

## ⚙️ Setup Guide

### Prerequisites
- Python 3.11+
- Node.js 18+

---

### Step 1 — Get API Keys (both free)

| Key | Where to get it |
|---|---|
| `GEMINI_API_KEY` | https://aistudio.google.com/app/apikey |
| `OPENWEATHER_API_KEY` | https://openweathermap.org/api |

---

### Step 2 — Configure Environment

```bash
# Copy the template
cp .env.example backend/.env

# Edit backend/.env and add your real keys
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXX
OPENWEATHER_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxx
CHROMA_PERSIST_DIR=./chroma_db
CHROMA_COLLECTION_NAME=agriculture_kb
```

---

### Step 3 — Backend Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

---

### Step 4 — Add Agriculture PDFs & Run Ingestion

Place agriculture PDF documents in `backend/ingestion/sources/`.

Recommended free PDFs:
- [FAO Rice Guide](https://www.fao.org/3/i2246e/i2246e.pdf)
- [FAO Wheat Guide](https://www.fao.org/3/y4011e/y4011e.pdf)
- [FAO Maize Guide](https://www.fao.org/3/y4391e/y4391e.pdf)
- [FAO Fertilizer Guide](https://www.fao.org/3/y4393e/y4393e.pdf)
- [FAO Irrigation Guide](https://www.fao.org/3/s2022e/s2022e.pdf)

Then run ingestion (runs **fully offline** using local embeddings — no API calls needed):

```bash
cd backend
python ingestion/ingest.py
```

> If interrupted, just run again — it auto-resumes from where it left off.

---

### Step 5 — Start the Backend

```bash
uvicorn main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

---

### Step 6 — Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

Open your browser at: **http://localhost:5173** 🎉

---

## 💬 Features

| Feature | How to Use |
|---|---|
| 🌱 General crop advice | Type any farming question in the chat |
| 🦠 Disease diagnosis (text) | Describe symptoms e.g. *"My wheat has yellow spots"* |
| 📷 Disease diagnosis (image) | Click 📷 to upload a leaf photo |
| 🌤️ Weather-aware advice | Click "Add location", enter your city |
| 💧 Fertilizer & irrigation | Ask e.g. *"How much nitrogen for rice per acre?"* |

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/chat` | General advisory chat |
| POST | `/api/diagnose/text` | Text-based disease diagnosis |
| POST | `/api/diagnose/image` | Image-based disease diagnosis |
| GET | `/api/weather?location=city` | Weather data |
| GET | `/health` | Health check |

---

## 🧪 Running Tests

```bash
cd backend
pytest tests/
```

---

## 🔒 Security Notes

- Never commit your `.env` file — it is gitignored by default
- The `.env.example` file contains only placeholder text — no real keys
- Rotate your API keys immediately if accidentally exposed

---

## 📄 License

MIT License — free to use, modify, and distribute.
