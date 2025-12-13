# How to Run

## Backend

```powershell
cd backend
poetry run backend
```

Backend will run on: http://localhost:8000

## Frontend

```powershell
cd frontend
poetry run frontend
```

Frontend will run on: http://localhost:8501

---

## First Time Setup

### Step 1: Install Dependencies

```powershell
cd backend
poetry install

cd ../frontend
poetry install
```

### Step 2: Download NLTK Data (Backend Only)

NLTK requires separate data files. After `poetry install`, run:

```powershell
cd backend
poetry run python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"
```

**Why?** Poetry installs the NLTK package, but NLTK data files (tokenizers, etc.) must be downloaded separately from NLTK's servers. See [SETUP_STEPS.md](SETUP_STEPS.md) for details.

## Notes

- The `poetry.lock` file and `.venv` folder are created in each project folder (`backend/` and `frontend/`)
- Poetry manages the virtual environment automatically - no need to activate it manually
- Use `poetry run <command>` to run commands in the virtual environment

