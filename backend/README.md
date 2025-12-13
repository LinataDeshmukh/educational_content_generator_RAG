# Learnify - Backend

FastAPI backend for the RAG-powered educational content generator.

## Setup

1. Install Poetry if you haven't already: https://python-poetry.org/docs/#installation

2. Install dependencies:
```bash
poetry install
```

3. Download NLTK data (required for text processing):
```bash
poetry run python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"
```

4. Create `.env` file in `backend/` directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=rag-educational-content
```

**Note:** The Pinecone index will be automatically created if it doesn't exist. You only need to provide your API key and region.

5. Run the development server:
```bash
poetry run backend
```

The API will be available at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`.

## Project Structure

```
backend/
├── fastapi_backend/          # Main backend package
│   ├── __main__.py          # Entry point (poetry run backend)
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration (Pydantic settings)
│   ├── dependencies.py      # Dependency injection
│   ├── middleware.py        # Exception handlers
│   ├── models/              # Data models
│   │   ├── document.py      # Document models
│   │   └── schemas.py       # Pydantic request/response schemas
│   ├── routers/             # API routes
│   │   ├── upload.py        # PDF upload endpoint
│   │   ├── chat.py          # Chat/Q&A endpoint
│   │   ├── quiz.py          # Quiz generation endpoint
│   │   ├── competitive_quiz.py  # Competitive quiz endpoints
│   │   ├── summary.py       # Summary generation endpoint
│   │   ├── flashcards.py    # Flashcard generation endpoint
│   │   └── documents.py     # Document listing endpoint
│   ├── services/            # Business logic
│   │   ├── rag_service.py   # RAG orchestration with LlamaIndex
│   │   ├── vector_store.py  # Pinecone integration (with auto-creation)
│   │   ├── content_generator.py  # Quiz, summary, flashcard generation
│   │   ├── competitive_quiz_service.py  # Adaptive quiz management
│   │   └── pdf_extractor.py  # PDF text extraction
│   └── utils/               # Utilities
│       ├── chunking.py      # Hybrid chunking strategy
│       ├── adaptive_learning.py  # Q-Learning & Thompson Sampling
│       └── errors.py        # Custom exceptions
└── pyproject.toml           # Poetry configuration
```

## Environment Variables

### Required

- `OPENAI_API_KEY`: Your OpenAI API key
- `PINECONE_API_KEY`: Your Pinecone API key

### Optional (with defaults)

- `PINECONE_ENVIRONMENT`: Pinecone region (default: `us-east-1`)
- `PINECONE_INDEX_NAME`: Name of your Pinecone index (default: `rag-educational-content`)
- `BACKEND_HOST`: Host to bind to (default: `0.0.0.0`)
- `BACKEND_PORT`: Port to bind to (default: `8000`)
- `LOG_LEVEL`: Logging level (default: `INFO`)
- `EMBEDDING_MODEL`: OpenAI embedding model (default: `text-embedding-3-small`)
- `LLM_MODEL`: OpenAI LLM model (default: `gpt-4o-mini`)
- `LLM_TEMPERATURE`: Temperature for LLM generation (default: `0.7`)
- `CORS_ORIGINS`: Allowed CORS origins (default: `["http://localhost:8501", "http://localhost:3000"]`)

## Key Features

### Pinecone Auto-Creation

The backend automatically creates the Pinecone index if it doesn't exist:
- Detects if index exists on startup
- Creates serverless index with correct dimensions (1536 for OpenAI embeddings)
- Waits for index to be ready before accepting requests
- Handles region configuration automatically

### Dependency Injection

Services are managed through dependency injection:
- Singleton pattern using `@lru_cache()`
- Clean separation of concerns
- Easy testing and mocking

### API Endpoints

- `POST /upload/` - Upload and index PDF documents
- `POST /chat` - Chat with documents using RAG
- `POST /quiz/` - Generate quizzes
- `POST /quiz/evaluate-answer` - Evaluate quiz answers
- `POST /competitive-quiz/generate-bank` - Generate question bank (30 questions)
- `POST /competitive-quiz/start` - Start competitive quiz
- `POST /competitive-quiz/answer` - Submit answer and get next question
- `POST /summary/` - Generate document summaries
- `POST /flashcards/` - Generate flashcards
- `GET /documents/list` - List all uploaded documents
- `GET /health` - Health check

### Error Handling

Comprehensive error handling for:
- PDF extraction errors
- Vector store operations
- RAG service errors
- Content generation failures
- API validation errors

All errors return structured JSON responses with appropriate HTTP status codes.

## Running the Server

### Development

```bash
poetry run backend
```

This uses uvicorn with auto-reload enabled.

### Production

```bash
poetry run uvicorn fastapi_backend.main:app --host 0.0.0.0 --port 8000
```

## Logging

The backend logs:
- Request/response information
- Pinecone initialization
- RAG operations
- Error details

Set `LOG_LEVEL` in `.env` to control verbosity (DEBUG, INFO, WARNING, ERROR).

## Testing

Test the API using the interactive docs at `http://localhost:8000/docs` or use curl:

```bash
# Health check
curl http://localhost:8000/health

# List documents
curl http://localhost:8000/documents/list
```

## Troubleshooting

### Pinecone Connection Issues

- Verify API key is correct in `.env`
- Check region matches your Pinecone account
- Check backend logs for initialization messages
- Index will be auto-created on first run

### NLTK Data Missing

If you see NLTK errors:
```bash
poetry run python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"
```

### Port Already in Use

Change the port in `.env`:
```env
BACKEND_PORT=8001
```

## License

This project is for educational purposes.
