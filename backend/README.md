# Language Agnostic Chatbot

A complete multilingual AI chatbot system powered by Retrieval-Augmented Generation (RAG). The platform allows administrators to upload institutional PDFs, automatically process and index their knowledge, and allows users to ask questions in any language. The system provides highly grounded answers with source references.

## Features
- **Multilingual Chatbot:** Seamlessly ask questions and receive answers in multiple languages.
- **PDF Knowledge Base:** Administrators can upload and manage PDF documents.
- **Automatic Document Processing:** Extracts text, cleans data, and generates intelligent vector embeddings.
- **Semantic + Keyword Retrieval:** Hybrid FAISS vector search combined with MongoDB keyword metadata.
- **RAG Architecture:** Grounded LLM generation using Google Gemini.
- **Source References:** Answers include the exact document title and page number used for context.
- **Chat History:** Persistent conversational flow managed in MongoDB.
- **Saved Answers:** Bookmark useful chatbot responses for later reference.
- **Live Updates:** Admin-published dynamic announcements with priority badging.
- **Notifications:** Notification center for users with unread badges and polling.
- **Admin Management:** Dedicated role-based access for managing documents and updates.
- **User Authentication:** Secure JWT-based registration and login system.

## Architecture

The system operates strictly on a separated front-end and back-end monolithic architecture.

**Chat & RAG Flow:**
`Frontend UI → FastAPI Backend → Language Detection → Embedding → FAISS (Semantic) + MongoDB (Keyword) → Context Reranking → Prompt Generation → LLM (Gemini) → Response Generation (with Sources) → Chat Persistence → UI`

**Live Updates & Notifications Flow:**
`Admin UI → FastAPI Backend → Create Update → Publish Update → MongoDB Status Update → Generate User Notifications → User Notification Polling → User UI`

## Installation

### Prerequisites
- Python 3.10+
- MongoDB instance (local or Atlas)
- Google Gemini API Key

### Backend Setup
1. Navigate to the `backend/` directory.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment.
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Copy the environment template:
   ```bash
   cp .env.example .env
   ```
6. Update `.env` with your secure credentials and keys.

### Frontend Setup
1. The frontend consists of pure HTML/CSS/JS.
2. Serve the `frontend/` directory using any static web server.
   ```bash
   cd frontend
   python -m http.server 8000
   ```
3. (Optional) Update `API_URL` in `app.js` if the backend is hosted differently.

## Environment Variables
The application requires several environment variables for security and integrations. See `.env.example` for details. 
- `JWT_SECRET`: Secure key for signing JWT tokens.
- `ADMIN_EMAIL` & `ADMIN_PASSWORD_HASH`: Static admin credentials.
- `MONGODB_URI` & `MONGODB_DB_NAME`: Database connection.
- `FAISS_INDEX_PATH`: Local directory for vector index persistence.
- `GEMINI_API_KEY`: Google Gemini API key.

## Running the Application

**Start the Backend:**
```bash
uvicorn app.main:app --reload --port 8080
```

**Start the Frontend:**
Open `frontend/login.html` in your browser (via a local web server).

## API Overview

The backend exposes several modular REST APIs:
- `/api/v1/auth/`: Registration, User Login, Admin Login, Profile fetching.
- `/api/v1/chat/`: Core RAG endpoint for processing user queries and retrieving answers.
- `/api/v1/chats/`: Manage conversational history (List, View, Soft-Delete).
- `/api/v1/saved-answers/`: Bookmark assistant responses.
- `/api/v1/documents/`: Admin document lifecycle management (Upload, Reprocess, Delete).
- `/api/v1/live-updates/`: Admin CRUD for dynamic platform updates.
- `/api/v1/notifications/`: User notification center (List, Mark Read, Unread Count).

## Testing

Run the automated test suite using pytest:
```bash
pytest tests/
```
*Note: Due to `pytest-asyncio` strict event loop scoping in integration with FastAPI/ASGI lifespan, some HTTP integration tests expecting mocked users without database seed records will return 401 Unauthorized instead of passing.*

## Deployment
- **Backend:** Can be deployed to any Python ASGI-compatible host (Render, Railway, Heroku, AWS). Requires persistent storage if FAISS indices are stored locally, or configure FAISS to rebuild/sync on startup.
- **Database:** Deploy MongoDB on MongoDB Atlas.
- **Frontend:** Deploy static files to Vercel, Netlify, or GitHub Pages.

## Known Limitations
- **FAISS Persistence:** Local FAISS storage requires a persistent disk on the hosting provider. If deployed to ephemeral serverless containers, FAISS index must be rebuilt or moved to a managed vector store (e.g. Pinecone).
- **Notification Polling:** Uses a 30-second interval polling mechanism. For high-scale enterprise applications, this could be migrated to WebSockets or SSE, but it is highly stable for the current monolithic architecture.
- **Test Harness Mocking:** FastAPI lifespan DB connection relies on ASGI lifecycle, which requires strict mock-user seeding in automated test fixtures.

## Final Security Notice
- Admin registration is strictly disabled.
- Ensure `.env` is never committed.
- All endpoints enforce strict User Data Isolation via backend JWT validation. User A cannot access User B's conversations or notifications.
