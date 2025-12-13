# Setup Steps After Poetry Install

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

### Step 1: Install Dependencies with Poetry

```powershell
# Backend
cd backend
poetry install

# Frontend  
cd ../frontend
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

Create `.env` files with your API keys:

**Backend `.env` file:**
```env
OPENAI_API_KEY=your_openai_key_here
PINECONE_API_KEY=your_pinecone_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment
PINECONE_INDEX_NAME=rag-educational-content
```

**Frontend `.env` file:**
```env
BACKEND_API_URL=http://localhost:8000
```

### Step 4: Run the Application

**Terminal 1 - Backend:**
```powershell
cd backend
poetry run backend
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
poetry run frontend
```

## Quick Setup Script

You can create a setup script to automate steps 1-2:

```powershell
# Setup script
cd backend
poetry install
poetry run python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"

cd ../frontend
poetry install
```

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

