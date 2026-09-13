# Crop Advisory Chatbot — Project Plan

## Top-Level Overview

**Goal:** Build a fully public, anonymous crop advisory chatbot as a web application that helps farmers and agricultural users get advice on crop selection, disease diagnosis (text and image), weather-based guidance, and fertilizer/irrigation recommendations.

**Approach:**
- React frontend with a clean chat UI and optional weather widget
- Python + FastAPI backend as the API layer
- LangChain orchestration layer with a RAG pipeline over a ChromaDB vector store
- Knowledge base seeded from public agriculture documents (FAO, ICAR, crop disease guides), chunked, embedded, and indexed
- GPT-4 (OpenAI API) as the primary LLM for response generation
- GPT-4 Vision (or similar multimodal model) for image-based disease diagnosis from leaf photos
- OpenWeatherMap API for real-time weather context injection
- No authentication — fully open, stateless chat sessions

**Scope:**
- Disease diagnosis (text description + image upload)
- Crop selection recommendations
- Weather-based advisory
- Fertilizer and irrigation recommendations
- Prompt guardrails to keep responses agricultural and factual

**Non-Goals:**
- Multi-language support (English only for now)
- User authentication or profile persistence
- Mobile native app (web only)
- Fine-tuning any LLM model

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React + TailwindCSS |
| Backend | Python 3.11 + FastAPI |
| Orchestration | LangChain |
| LLM | OpenAI GPT-4 (text) + GPT-4 Vision (image) |
| Embeddings | OpenAI text-embedding-3-small |
| Vector Store | ChromaDB (local persistent) |
| Knowledge Base | Public PDFs — FAO, ICAR, crop disease guides |
| Weather | OpenWeatherMap API |
| File Upload | FastAPI multipart + local temp storage |

---

## Sub-Tasks

---

### Sub-Task 1 — Project Scaffold

**Status:** `[x] done`

**Intent:**
Set up the complete folder structure for both frontend and backend so all subsequent sub-tasks have a consistent, well-organised base to build on.

**Expected Outcomes:**
- `frontend/` contains a bootstrapped React app with TailwindCSS configured
- `backend/` contains a FastAPI project with environment config, a requirements file, and a clear module layout
- A root `README.md` documents how to run both services locally
- A `.env.example` file documents all required environment variables

**Todo List:**
1. Create root project directory with `frontend/` and `backend/` sub-directories
2. Bootstrap React app in `frontend/` using Vite (`npm create vite@latest`) with TypeScript template
3. Install and configure TailwindCSS in the React app
4. Create `backend/` Python project with the following module structure:
   - `main.py` — FastAPI app entry point
   - `api/` — route handlers
   - `services/` — domain services (rag, weather, disease, advisory)
   - `ingestion/` — knowledge base loading and indexing scripts
   - `config.py` — environment variable loading via `python-dotenv`
5. Create `requirements.txt` with all backend dependencies:
   `fastapi`, `uvicorn`, `langchain`, `langchain-openai`, `langchain-chroma`,
   `chromadb`, `openai`, `python-dotenv`, `httpx`, `Pillow`, `pypdf`
6. Create `.env.example` documenting: `OPENAI_API_KEY`, `OPENWEATHER_API_KEY`, `CHROMA_PERSIST_DIR`
7. Add CORS middleware to FastAPI to allow the React dev server origin
8. Create root `README.md` with setup and run instructions for both services

**Relevant Context:**
- Backend entry point: `backend/main.py`
- Config loading: `backend/config.py`
- Environment template: `.env.example`

---

### Sub-Task 2 — Knowledge Base Ingestion Pipeline

**Status:** `[x] done`

**Intent:**
Download or place public agriculture documents (FAO crop guides, ICAR advisories, crop disease identification guides) into the system, chunk them into meaningful passages, embed them using OpenAI embeddings, and persist them into ChromaDB. This is the foundation of the RAG pipeline.

**Expected Outcomes:**
- A script `backend/ingestion/ingest.py` that loads, chunks, embeds, and indexes all source documents
- A populated ChromaDB collection persisted to disk at the path defined by `CHROMA_PERSIST_DIR`
- Documents are chunked at ~500 tokens with 50-token overlap to preserve context across chunk boundaries
- Metadata (source document, page number, topic category) is stored per chunk for citation in responses

**Todo List:**
1. Create `backend/ingestion/` directory with `ingest.py` and a `sources/` folder for raw PDFs
2. Collect and place source documents in `backend/ingestion/sources/`:
   - FAO crop production guides (wheat, rice, maize, cotton, vegetables)
   - ICAR crop advisory bulletins
   - Crop disease identification and management guides (at least 5–10 common diseases)
3. Implement document loading using LangChain's `PyPDFLoader` (for PDFs)
4. Implement text splitting using `RecursiveCharacterTextSplitter` with `chunk_size=500`, `chunk_overlap=50`
5. Tag each chunk with metadata: `source`, `page`, `category` (e.g. "disease", "crop", "fertilizer", "weather")
6. Embed chunks using `OpenAIEmbeddings` with model `text-embedding-3-small`
7. Persist embeddings into a named ChromaDB collection (e.g. `agriculture_kb`) at `CHROMA_PERSIST_DIR`
8. Add a simple `--reset` flag to the ingestion script to wipe and re-index the collection
9. Test ingestion script end-to-end and verify document count in the ChromaDB collection

**Relevant Context:**
- Ingestion script: `backend/ingestion/ingest.py`
- Source documents directory: `backend/ingestion/sources/`
- LangChain loaders: `langchain_community.document_loaders.PyPDFLoader`
- Vector store: `langchain_chroma.Chroma`

---

### Sub-Task 3 — RAG Pipeline (Core Retrieval + LLM Chain)

**Status:** `[x] done`

**Intent:**
Build the core RAG pipeline that, given a user query, retrieves the most relevant knowledge base chunks from ChromaDB and passes them as grounded context to GPT-4 to generate an accurate, agriculture-specific answer. This service is the intelligence core of the chatbot.

**Expected Outcomes:**
- A `backend/services/rag_service.py` module exposing a `query(user_input: str) -> str` function
- Retrieval fetches top-5 most relevant chunks from ChromaDB by cosine similarity
- A well-structured system prompt instructs GPT-4 to act as an agriculture expert and to base answers only on retrieved context
- If retrieval yields no relevant context, the LLM responds with a clear fallback message (e.g. "I don't have specific information on that — please consult a local agronomist")
- Response includes source citations (document name) where available

**Todo List:**
1. Create `backend/services/rag_service.py`
2. Load the persisted ChromaDB collection using `Chroma` with the same embedding model used during ingestion
3. Build a LangChain retriever from the ChromaDB collection (`as_retriever(search_kwargs={"k": 5})`)
4. Design the system prompt for the LLM:
   - Role: "You are an expert agricultural advisor helping farmers."
   - Instruction: "Answer only based on the provided context. If the context does not contain enough information, say so clearly."
   - Format guidance: "Give concise, practical, actionable advice."
5. Implement the RAG chain using LangChain's `RetrievalQA` or `create_retrieval_chain` with `ChatOpenAI(model="gpt-4")`
6. Add source document citation extraction from the chain's `source_documents` output
7. Wrap in a `query(user_input: str) -> dict` function returning `{"answer": str, "sources": list[str]}`
8. Write a quick smoke test in `backend/tests/test_rag.py` to verify the chain returns a sensible answer

**Relevant Context:**
- RAG service: `backend/services/rag_service.py`
- LangChain chain: `langchain.chains.RetrievalQA` or `langchain.chains.combine_documents`
- LLM wrapper: `langchain_openai.ChatOpenAI`

---

### Sub-Task 4 — Disease Diagnosis Service (Text + Image)

**Status:** `[x] done`

**Intent:**
Build a disease diagnosis service that accepts either a text description of crop symptoms or an uploaded leaf/plant image (or both) and returns a likely disease identification with management recommendations. Image analysis uses GPT-4 Vision for visual diagnosis, with the result then augmented by the RAG pipeline for treatment advice.

**Expected Outcomes:**
- A `backend/services/disease_service.py` module with:
  - `diagnose_from_text(crop: str, symptoms: str) -> dict`
  - `diagnose_from_image(image_bytes: bytes, crop: str) -> dict`
- Image diagnosis encodes the image in base64 and sends it to GPT-4 Vision with a structured prompt asking for disease identification
- The raw diagnosis result is then passed back through the RAG pipeline to fetch treatment/management recommendations
- The final response contains: `disease_name`, `confidence`, `description`, `management_steps`, `sources`

**Todo List:**
1. Create `backend/services/disease_service.py`
2. Implement `diagnose_from_text(crop, symptoms)`:
   - Build a query string combining crop name and symptom description
   - Pass to `rag_service.query()` and return structured result
3. Implement `diagnose_from_image(image_bytes, crop)`:
   - Encode image bytes to base64
   - Call OpenAI Chat Completions API with `model="gpt-4-vision-preview"` and an image content block
   - Prompt: "You are an expert plant pathologist. Identify the disease visible in this crop image and describe the symptoms."
   - Parse the LLM's disease identification text
   - Pass the identified disease name back to `rag_service.query()` for management recommendations
4. Standardise the return schema: `{"disease_name": str, "description": str, "management_steps": list[str], "sources": list[str]}`
5. Add a FastAPI route in `backend/api/disease_router.py`:
   - `POST /api/diagnose/text` — accepts `crop` and `symptoms` as JSON body
   - `POST /api/diagnose/image` — accepts multipart form with `crop` (text field) and `image` (file)
6. Add input validation: reject non-image file types, limit image size to 5MB

**Relevant Context:**
- Disease service: `backend/services/disease_service.py`
- Router: `backend/api/disease_router.py`
- OpenAI Vision API: `openai.ChatCompletion` with `content` list containing `image_url` (base64 encoded)

---

### Sub-Task 5 — Weather Integration Service

**Status:** `[x] done`

**Intent:**
Integrate OpenWeatherMap to fetch current weather and a 5-day forecast for a user-provided location. Inject this weather data as additional context into advisory prompts so the LLM can provide weather-aware recommendations (e.g. "Given rain is forecast this week, delay irrigation").

**Expected Outcomes:**
- A `backend/services/weather_service.py` module exposing `get_weather_context(location: str) -> str`
- Returns a formatted weather summary string ready to be injected into LLM prompts
- A FastAPI route `GET /api/weather?location=<city>` for the frontend weather widget
- Graceful fallback if the location is invalid or the weather API is unreachable

**Todo List:**
1. Create `backend/services/weather_service.py`
2. Implement `get_current_weather(location: str) -> dict` using `httpx` to call OpenWeatherMap's Current Weather API
3. Implement `get_forecast(location: str) -> list[dict]` using the 5-day / 3-hour Forecast API
4. Implement `get_weather_context(location: str) -> str` that formats the weather data into a concise summary string:
   - Example: "Current weather in Pune: 28°C, partly cloudy, humidity 72%. Forecast: rain expected in 2 days."
5. Add error handling: return `""` (empty string, no context injected) if location lookup fails
6. Create `backend/api/weather_router.py` with `GET /api/weather?location=<city>` endpoint
7. Register the weather router in `main.py`

**Relevant Context:**
- Weather service: `backend/services/weather_service.py`
- Router: `backend/api/weather_router.py`
- OpenWeatherMap API docs: `https://openweathermap.org/api`

---

### Sub-Task 6 — Chat Orchestration API Endpoint

**Status:** `[x] done`

**Intent:**
Build the main chat endpoint that receives a user message (and optional location), orchestrates the RAG pipeline, weather context injection, and domain service routing, and returns a coherent, grounded response. This is the single integration point that ties all backend services together.

**Expected Outcomes:**
- A `POST /api/chat` endpoint defined in `backend/api/chat_router.py`
- Request body: `{ "message": str, "location": str | null, "session_id": str | null }`
- Response body: `{ "response": str, "sources": list[str], "weather_context": str | null }`
- The orchestration layer injects weather context into the prompt when a location is provided
- Intent routing: if the message contains disease/symptom keywords, route to the disease service; otherwise route to the RAG service
- Simple keyword-based intent detection is sufficient (no ML classifier needed at this stage)

**Todo List:**
1. Create `backend/api/chat_router.py` with `POST /api/chat`
2. Define Pydantic request/response models: `ChatRequest`, `ChatResponse`
3. Implement simple intent detection in `backend/services/intent_service.py`:
   - Keywords for disease intent: "disease", "pest", "yellowing", "spots", "wilting", "fungal", "infected", "symptom"
   - Keywords for weather intent: "rain", "drought", "temperature", "irrigation", "weather"
   - Default: route to general RAG advisory
4. If `location` is provided, call `weather_service.get_weather_context(location)` and prepend it to the user query before passing to the RAG chain
5. If disease intent detected, call `disease_service.diagnose_from_text(crop, symptoms)` — extract crop name from the message using a simple prompt to GPT-4
6. Otherwise call `rag_service.query(user_input)` for general advisory
7. Register the chat router in `backend/main.py`
8. Add basic rate limiting (e.g. 20 requests/minute per IP using `slowapi`) to prevent API abuse

**Relevant Context:**
- Chat router: `backend/api/chat_router.py`
- Intent service: `backend/services/intent_service.py`
- All services wired through: `backend/main.py`

---

### Sub-Task 7 — React Chat UI

**Status:** `[x] done`

**Intent:**
Build the user-facing chat interface in React — a clean, responsive chat window where users can type messages, optionally provide their location for weather-aware advice, and upload leaf images for disease diagnosis.

**Expected Outcomes:**
- A working chat UI at `http://localhost:5173` (Vite dev server)
- Message bubbles distinguish user messages from bot responses
- A location input field that enriches responses with weather context
- An image upload button within the chat input for disease diagnosis
- Sources/citations displayed below advisory responses when available
- A weather widget showing current conditions if a location is set
- Responsive design that works on desktop and tablet

**Todo List:**
1. Create the following React component structure inside `frontend/src/`:
   - `components/ChatWindow.tsx` — main chat container
   - `components/MessageBubble.tsx` — individual message display with role styling
   - `components/ChatInput.tsx` — text input, location field, image upload button, send button
   - `components/WeatherWidget.tsx` — displays current weather for the set location
   - `components/SourcesList.tsx` — renders cited source document names below a response
2. Implement chat state management in `ChatWindow.tsx`:
   - Messages array with `role: "user" | "bot"` and `content: string`
   - Loading indicator while awaiting API response
   - Auto-scroll to latest message
3. Implement `ChatInput.tsx`:
   - Text input for the message
   - Optional location text field (collapsible or inline)
   - File input for image upload (accept `image/*`, max 5MB client-side check)
   - On submit: if image attached, call `POST /api/diagnose/image`; otherwise call `POST /api/chat`
4. Implement `WeatherWidget.tsx`:
   - Calls `GET /api/weather?location=<city>` when location changes
   - Displays temperature, condition, and humidity
5. Add a typed API client in `frontend/src/api/chatApi.ts` with functions:
   - `sendMessage(message, location)` — calls `POST /api/chat`
   - `diagnoseImage(formData)` — calls `POST /api/diagnose/image`
   - `getWeather(location)` — calls `GET /api/weather`
6. Style with TailwindCSS — clean green/earthy color theme fitting an agriculture product

**Relevant Context:**
- Frontend entry: `frontend/src/main.tsx`
- API client: `frontend/src/api/chatApi.ts`
- Vite proxy config: `frontend/vite.config.ts` (proxy `/api` to `http://localhost:8000`)

---

### Sub-Task 8 — Prompt Engineering and Guardrails

**Status:** `[x] done`

**Intent:**
Tune all LLM system prompts for agricultural accuracy, add guardrails that prevent off-topic responses, and implement fallback handling for low-confidence or out-of-scope queries. This ensures the chatbot stays focused and trustworthy.

**Expected Outcomes:**
- All prompts stored in a dedicated `backend/prompts/` directory as string constants or Jinja2 templates
- The chatbot refuses to answer clearly non-agricultural questions (e.g. politics, coding) with a polite redirect
- Responses are structured, concise, and actionable — not generic LLM prose
- A "disclaimer" is appended to high-risk advice (e.g. pesticide use) recommending consultation with a local agronomist

**Todo List:**
1. Create `backend/prompts/` directory with prompt constants:
   - `system_prompt.py` — base agriculture expert system prompt
   - `disease_prompt.py` — disease diagnosis prompt for GPT-4 Vision
   - `advisory_prompt.py` — general crop advisory prompt with weather context template
2. Update `rag_service.py` to use prompts from `backend/prompts/system_prompt.py`
3. Add topic guardrail: if the retrieved context relevance score is below a threshold (e.g. cosine similarity < 0.35 for all chunks), return a fallback message instead of hallucinating
4. Add off-topic detection: if LangChain retrieval returns 0 relevant chunks and message does not match agriculture keywords, respond with: "I specialise in crop advisory. Please ask me about crops, diseases, fertilizers, irrigation, or weather-based farming advice."
5. Add disclaimer for pesticide/chemical recommendations: append "⚠️ For pesticide application, always consult a certified agronomist and follow local regulations."
6. Test prompts with at least 10 representative user queries covering all advisory domains

**Relevant Context:**
- Prompts directory: `backend/prompts/`
- RAG service: `backend/services/rag_service.py`
- Similarity score access: ChromaDB retriever returns scores via `similarity_search_with_score`

---

### Sub-Task 9 — Testing and Validation

**Status:** `[x] done`

**Intent:**
Write tests for all critical backend services and do an end-to-end validation of the full chatbot flow to ensure the system is reliable before any deployment.

**Expected Outcomes:**
- Unit tests for RAG service, disease service, weather service, and intent detection
- Integration test for the `POST /api/chat` endpoint covering at least 5 advisory scenarios
- All tests pass with `pytest` from the `backend/` directory

**Todo List:**
1. Create `backend/tests/` directory with `conftest.py` setting up a test FastAPI client and mocking OpenAI/weather API calls
2. Write `test_rag.py`: test that `rag_service.query()` returns a non-empty answer and a non-empty sources list for at least 3 known agricultural queries
3. Write `test_disease.py`: test `diagnose_from_text()` with a known symptom description; mock GPT-4 Vision response for `diagnose_from_image()`
4. Write `test_weather.py`: mock OpenWeatherMap API and verify `get_weather_context()` returns a formatted string
5. Write `test_intent.py`: verify intent detection correctly routes disease keywords vs general queries
6. Write `test_chat_endpoint.py`: integration tests for `POST /api/chat` covering:
   - General crop advisory query
   - Disease symptom query with intent routing
   - Query with location (weather context injected)
   - Off-topic query (guardrail fires)
   - Empty message (input validation)
7. Run `pytest backend/tests/` and confirm all tests pass
8. Do a manual end-to-end test: open the React app, send 5 different advisory queries, upload one leaf image, and verify quality of responses

**Relevant Context:**
- Test directory: `backend/tests/`
- FastAPI test client: `fastapi.testclient.TestClient`
- Mocking: `unittest.mock.patch` for OpenAI and httpx calls

---

## Implementation Order

Sub-tasks must be completed in this order, as each builds on the previous:

1. Project Scaffold
2. Knowledge Base Ingestion Pipeline
3. RAG Pipeline
4. Disease Diagnosis Service
5. Weather Integration Service
6. Chat Orchestration API Endpoint
7. React Chat UI
8. Prompt Engineering and Guardrails
9. Testing and Validation

---

## Environment Variables Required

```
OPENAI_API_KEY=<your OpenAI API key>
OPENWEATHER_API_KEY=<your OpenWeatherMap API key>
CHROMA_PERSIST_DIR=./backend/chroma_db
```
