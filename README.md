# Crop Advisory Chatbot

An AI-powered crop advisory web application that helps farmers get advice on crop selection, disease diagnosis, weather-based guidance, and fertilizer/irrigation recommendations.

## Architecture

- **Frontend**: React + TypeScript + TailwindCSS (Vite)
- **Backend**: Python + FastAPI
- **Orchestration**: LangChain
- **LLM**: OpenAI GPT-4 (text) + GPT-4 Vision (image disease diagnosis)
- **Vector Store**: ChromaDB (local persistent)
- **Knowledge Base**: Public agriculture documents (FAO, ICAR, crop disease guides)
- **Weather**: OpenWeatherMap API

## Project Structure

```
crop-advisory-chatbot/
├── frontend/               # React + Vite frontend
│   ├── src/
│   │   ├── api/            # Typed API client
│   │   ├── components/     # React components
│   │   └── types/          # TypeScript types
│   └── package.json
├── backend/                # FastAPI backend
│   ├── api/                # Route handlers
│   ├── services/           # Domain services (RAG, disease, weather, intent)
│   ├── ingestion/          # Knowledge base loading and indexing
│   │   └── sources/        # Place source PDFs here
│   ├── prompts/            # LLM prompt templates
│   ├── tests/              # pytest tests
│   ├── config.py           # Environment configuration
│   ├── main.py             # FastAPI app entry point
│   └── requirements.txt
├── .env.example            # Environment variable template
└── crop-advisory-chatbot-plan.md  # Full project plan
```

## Setup

### 1. Environment Variables

Copy `.env.example` to `backend/.env` and fill in your API keys:

```bash
cp .env.example backend/.env
```

Required keys:
- `OPENAI_API_KEY` — [OpenAI API Key](https://platform.openai.com/api-keys)
- `OPENWEATHER_API_KEY` — [OpenWeatherMap API Key](https://openweathermap.org/api)

### 2. Backend Setup

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Ingest the Knowledge Base

Place agriculture PDF documents in `backend/ingestion/sources/`, then run:

```bash
cd backend
python ingestion/ingest.py
```

Use `--reset` to wipe and re-index:

```bash
python ingestion/ingest.py --reset
```

### 4. Start the Backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

API docs available at: [http://localhost:8000/docs](http://localhost:8000/docs)

### 5. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

App available at: [http://localhost:5173](http://localhost:5173)

## Features

| Feature | How to Use |
|---|---|
| General crop advice | Type your question in the chat |
| Disease diagnosis (text) | Describe symptoms (e.g. "My wheat has yellow spots") |
| Disease diagnosis (image) | Click 📷 to upload a leaf photo |
| Weather-aware advice | Click "Add location" and enter your city |
| Fertilizer/irrigation advice | Ask naturally (e.g. "How much fertilizer for rice?") |

## Running Tests

```bash
cd backend
pytest tests/
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/chat` | General advisory chat |
| POST | `/api/diagnose/text` | Text-based disease diagnosis |
| POST | `/api/diagnose/image` | Image-based disease diagnosis |
| GET | `/api/weather?location=<city>` | Current weather and forecast |
| GET | `/health` | Health check |
