# RAG Educational Content Generator - Frontend

Streamlit frontend for the RAG-powered educational content generator.

## Quick Start

### Simple Way (Recommended)

Just run:
```bash
cd frontend
streamlit run src/streamlit_app/main.py
```

The app will automatically handle the Python path setup.

### Alternative: Using Python

```bash
cd frontend
python -m streamlit run src/streamlit_app/main.py
```

## Setup

1. Install dependencies:
```bash
pip install streamlit requests httpx python-dotenv
```

2. Make sure your `.env` file has:
```
BACKEND_API_URL=http://localhost:8000
```

3. Make sure the backend is running on port 8000

## Running

1. Start the backend first (in a separate terminal)
2. Then run the frontend using the command above
3. The app will open automatically in your browser at `http://localhost:8501`
