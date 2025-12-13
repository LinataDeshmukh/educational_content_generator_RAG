# How to Run

## Quick Start

### Backend

```powershell
cd backend
poetry run backend
```

Backend will run on: http://localhost:8000

**First time setup:**
```powershell
cd backend
poetry install
poetry run python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"
```

Create `.env` file in `backend/`:
```env
OPENAI_API_KEY=your_openai_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=rag-educational-content
```

**Note:** The Pinecone index will be automatically created if it doesn't exist. You only need your API key and region.

### Frontend (Next.js - Recommended)

```powershell
cd frontend_v2
npm install   # First time only
npm run dev
```

Frontend will run on: http://localhost:3000

**First time setup:**
1. Create `.env.local` file in `frontend_v2/`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

2. Install dependencies:
```powershell
npm install
```

### Frontend (Streamlit - Legacy)

```powershell
cd frontend
poetry run frontend
```

Frontend will run on: http://localhost:8501

**First time setup:**
```powershell
cd frontend
poetry install
```

Create `.env` file in `frontend/`:
```env
BACKEND_API_URL=http://localhost:8000
```

---

## Complete Setup Guide

For detailed setup instructions, see [SETUP_STEPS.md](SETUP_STEPS.md).

## Features

- **PDF Upload**: Upload and index PDF documents (up to 300 pages)
- **Chat**: Ask questions about your documents with RAG-powered answers
- **Quiz**: Generate quizzes with detailed statistical analysis and visual charts
- **Competitive Quiz**: Adaptive difficulty quiz (30 questions) with comprehensive analytics
- **Summary**: Generate summaries of varying lengths
- **Flashcards**: Create flashcards for studying

## Notes

- The backend uses Poetry for dependency management
- The Next.js frontend uses npm for dependency management
- Pinecone index is automatically created if it doesn't exist
- Document names are displayed throughout the application
- All statistics include visual charts and progress bars
