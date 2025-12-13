# Setup Steps After Poetry Install

## Overview

This project has two frontends:
- **Next.js Frontend** (`frontend_v2/`) - Recommended, modern React application
- **Streamlit Frontend** (`frontend/`) - Legacy Python-based UI

## What is NLTK?

**NLTK (Natural Language Toolkit)** is a Python library for natural language processing. In this project, it's used by `llama-index` for:
- **Text tokenization** - Breaking text into words/sentences
- **Language processing** - Understanding text structure

## Why Poetry Can't Install NLTK Data

Poetry **CAN** install the NLTK Python package, but it **CANNOT** automatically download NLTK's data files because:

1. **Data files are separate** - NLTK package (~2MB) vs data files (100+ MB)
2. **Downloaded from NLTK servers** - Not from PyPI (Python Package Index)
3. **User choice** - NLTK lets you download only what you need
4. **Large size** - Would bloat the package if included

## Complete Setup Steps

### Step 1: Install Backend Dependencies

```powershell
cd backend
poetry install
```

### Step 2: Download NLTK Data (Backend Only)

After `poetry install`, you need to download NLTK data files:

```powershell
cd backend
poetry run python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"
```

**What this does:**
- Downloads `punkt` - Sentence tokenizer
- Downloads `punkt_tab` - Tabular tokenizer data
- Stores in: `C:\Users\YourName\AppData\Roaming\nltk_data`

**Alternative - Download all NLTK data (optional):**
```powershell
poetry run python -c "import nltk; nltk.download('all')"
```
⚠️ This downloads ~500MB of data - only do this if you need everything.

### Step 3: Set Up Environment Variables

**Backend `.env` file** (create in `backend/` directory):
```env
OPENAI_API_KEY=your_openai_key_here
PINECONE_API_KEY=your_pinecone_key_here
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=rag-educational-content
```

**Important Notes:**
- The Pinecone index will be **automatically created** if it doesn't exist
- You only need to provide your API key and region (e.g., `us-east-1`)
- Get your Pinecone API key from [app.pinecone.io](https://app.pinecone.io)

**Frontend (Next.js) `.env.local` file** (create in `frontend_v2/` directory):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Frontend (Streamlit) `.env` file** (create in `frontend/` directory):
```env
BACKEND_API_URL=http://localhost:8000
```

### Step 4: Run the Application

**Terminal 1 - Backend:**
```powershell
cd backend
poetry run backend
```

The backend will:
- Initialize Pinecone (auto-creates index if needed)
- Start FastAPI server on http://localhost:8000
- Show registered routes in logs

**Terminal 2 - Frontend (Next.js - Recommended):**
```powershell
cd frontend_v2
npm install   # First time only
npm run dev
```

The Next.js frontend runs on http://localhost:3000

**Terminal 2 - Frontend (Streamlit - Legacy):**
```powershell
cd frontend
poetry install   # First time only
poetry run frontend
```

The Streamlit frontend runs on http://localhost:8501

## Quick Setup Script

You can create a setup script to automate steps 1-2:

```powershell
# Setup script
cd backend
poetry install
poetry run python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"

cd ../frontend
poetry install

cd ../frontend_v2
npm install
```

## Project Structure

```
backend/
├── fastapi_backend/        # Main backend package
│   ├── main.py            # FastAPI application
│   ├── routers/           # API endpoints
│   ├── services/          # Business logic
│   └── ...
└── pyproject.toml

frontend_v2/               # Next.js frontend (recommended)
├── app/                   # Next.js pages
├── components/            # React components
├── lib/                   # Utilities and API client
└── package.json

frontend/                  # Streamlit frontend (legacy)
└── streamlit_frontend/
```

## Key Features

### Backend
- **FastAPI** with clean router structure
- **Pinecone auto-creation** - Index created automatically if missing
- **Dependency injection** - Clean service management
- **Poetry** - Dependency management

### Frontend (Next.js)
- **Next.js 14** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **Zustand** for state management
- **Light/Dark mode** support
- **Visual statistics** with charts and progress bars

### Statistics & Analytics
- **Quiz Statistics**: Detailed performance analysis with visual charts
- **Competitive Quiz Analytics**: Comprehensive statistics with difficulty breakdown
- **Progress Tracking**: Real-time progress bars and visual indicators
- **Answer History**: Visual grid representation of quiz answers

## Troubleshooting

### NLTK Data Not Found Error

If you see `Resource punkt not found`:
```powershell
cd backend
poetry run python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"
```

### Check NLTK Data Location

```powershell
poetry run python -c "import nltk; print(nltk.data.path)"
```

### Re-download NLTK Data

If data is corrupted:
```powershell
poetry run python -c "import nltk; nltk.download('punkt', force=True); nltk.download('punkt_tab', force=True)"
```

### Pinecone Index Issues

If you see Pinecone errors:
1. Check your API key in `.env` file
2. Verify the region (e.g., `us-east-1`)
3. The index will be auto-created on first run
4. Check backend logs for initialization messages

### Frontend Connection Issues

If the frontend can't connect to backend:
1. Ensure backend is running on http://localhost:8000
2. Check `.env.local` (Next.js) or `.env` (Streamlit) has correct `BACKEND_API_URL`
3. Check browser console for CORS errors
4. Verify backend logs show the request

### Node.js/npm Issues

If `npm` is not recognized:
1. Install Node.js from [nodejs.org](https://nodejs.org/)
2. Restart your terminal
3. Verify: `node --version` and `npm --version`

## Next Steps

1. Upload a PDF document
2. Try the Chat feature
3. Generate a Quiz and view the statistics
4. Try the Competitive Quiz (30 questions) with adaptive difficulty
5. Explore Summary and Flashcards features

For more information, see [README.md](README.md).
