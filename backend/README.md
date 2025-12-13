# RAG Educational Content Generator - Backend

FastAPI backend for the RAG-powered educational content generator.

## Setup

1. Install Poetry if you haven't already: https://python-poetry.org/docs/#installation

2. Install dependencies:
```bash
poetry install
```

3. Copy `.env.example` to `.env` and fill in your API keys:
```bash
cp .env.example .env
```

4. Run the development server:
```bash
poetry run uvicorn rag_edu_generator.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`.

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `PINECONE_API_KEY`: Your Pinecone API key
- `PINECONE_ENVIRONMENT`: Your Pinecone environment (e.g., "us-east1-gcp")
- `PINECONE_INDEX_NAME`: Name of your Pinecone index
- `BACKEND_HOST`: Host to bind to (default: 0.0.0.0)
- `BACKEND_PORT`: Port to bind to (default: 8000)
- `LOG_LEVEL`: Logging level (default: INFO)
- `EMBEDDING_MODEL`: OpenAI embedding model to use (default: text-embedding-3-small)
- `LLM_MODEL`: OpenAI LLM model to use (default: gpt-4-turbo-preview)
- `LLM_TEMPERATURE`: Temperature for LLM generation (default: 0.7)

