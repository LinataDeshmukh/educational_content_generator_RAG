# RAG-Powered Educational Content Generator

A comprehensive application that uses RAG (Retrieval-Augmented Generation) to help students and educators interact with PDF educational materials. Upload a PDF, and the system enables you to chat with the material, generate quizzes, summaries, and flashcards.

## Features

- **PDF Processing**: Upload and index multiple PDF documents (up to 300 pages total)
- **Document Persistence**: Continue with previously uploaded documents to save API credits
- **Chat Interface**: Ask questions about the material with RAG-powered answers, intelligent fallback, and systematic prompting
- **Quiz Generation**: Generate contextual quizzes with hints, LLM-based evaluation, and detailed performance analytics
- **Competitive Quiz**: Adaptive difficulty quiz system using Q-Learning and Thompson Sampling algorithms
- **Summary Generation**: Create comprehensive summaries (short, medium, or long)
- **Flashcard Generation**: Generate flashcards for studying key concepts

## Architecture

The project consists of two separate Poetry projects:

- **Backend** (`backend/`): FastAPI application with RAG pipeline
- **Frontend** (`frontend/`): Streamlit UI application

## Tech Stack

### Backend
- FastAPI - REST API framework
- LlamaIndex - RAG orchestration
- Pinecone - Vector database (with namespace isolation)
- PyMuPDF - PDF text extraction
- OpenAI - Embeddings and LLM
- NumPy - Adaptive learning algorithms

### Frontend
- Streamlit - Web UI framework
- httpx - HTTP client for API communication
- Matplotlib & Pandas - Data visualization for quiz analytics

## Setup

### Prerequisites

- Python 3.9+
- Poetry (https://python-poetry.org/docs/#installation)
- OpenAI API key
- Pinecone API key and account

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
poetry install
```

3. Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
```

Edit `.env` with your API keys:
```
OPENAI_API_KEY=your_openai_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment_here
PINECONE_INDEX_NAME=rag-educational-content
```

4. Run the backend server:
```bash
poetry run uvicorn rag_edu_generator.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`.

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
poetry install
```

3. Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
```

Edit `.env`:
```
BACKEND_API_URL=http://localhost:8000
```

4. Run the Streamlit app:
```bash
poetry run streamlit run src/streamlit_app/main.py
```

The app will be available at `http://localhost:8501`.

## Usage

1. **Upload PDF(s)**: Go to the Upload page and upload one or multiple PDF documents (up to 300 pages total)
   - Option to continue with previously uploaded documents
2. **Chat**: Use the Chat page to ask questions about the material with intelligent RAG responses
3. **Generate Quiz**: Create contextual quizzes with hints and detailed performance reports
4. **Competitive Quiz**: Experience adaptive difficulty quizzes that adjust based on your performance using Q-Learning and Thompson Sampling
5. **Generate Summary**: Get summaries of varying lengths (short, medium, long)
6. **Generate Flashcards**: Create flashcards for studying key concepts

## Project Structure

```
RAG-Powered Educational Content Generator/
├── backend/
│   ├── src/rag_edu_generator/
│   │   ├── main.py                    # FastAPI app
│   │   ├── config.py                  # Configuration
│   │   ├── models/                    # Data models (Pydantic schemas)
│   │   ├── services/                  # Business logic
│   │   │   ├── rag_service.py         # RAG orchestration
│   │   │   ├── vector_store.py        # Pinecone integration
│   │   │   ├── content_generator.py   # Quiz, summary, flashcard generation
│   │   │   ├── competitive_quiz_service.py  # Adaptive quiz management
│   │   │   └── pdf_extractor.py       # PDF text extraction
│   │   ├── api/                       # API routes
│   │   │   ├── routes/
│   │   │   │   ├── upload.py          # PDF upload endpoint
│   │   │   │   ├── chat.py            # Chat/Q&A endpoint
│   │   │   │   ├── quiz.py            # Quiz generation endpoint
│   │   │   │   ├── competitive_quiz.py  # Competitive quiz endpoints
│   │   │   │   ├── summary.py         # Summary generation endpoint
│   │   │   │   ├── flashcards.py          # Flashcard generation endpoint
│   │   │   │   └── documents.py       # Document listing endpoint
│   │   │   └── middleware.py          # Exception handling
│   │   └── utils/                     # Utilities
│   │       ├── chunking.py            # Hybrid chunking strategy
│   │       ├── adaptive_learning.py   # Q-Learning & Thompson Sampling
│   │       └── errors.py              # Custom exceptions
│   └── pyproject.toml
├── frontend/
│   ├── src/streamlit_app/
│   │   ├── main.py                    # Streamlit app entry point
│   │   ├── pages/                     # UI pages
│   │   │   ├── upload.py              # PDF upload page
│   │   │   ├── chat.py                # Chat interface
│   │   │   ├── quiz.py                # Quiz generation & taking
│   │   │   ├── competitive_quiz.py    # Adaptive competitive quiz
│   │   │   ├── summary.py             # Summary generation
│   │   │   └── flashcards.py          # Flashcard study interface
│   │   └── utils/
│   │       └── api_client.py          # HTTP client for backend
│   └── pyproject.toml
├── docs/                              # GitHub Pages website
│   ├── index.html
│   ├── styles.css
│   ├── script.js
│   └── README.md
├── project_documentation/             # Project documentation
│   ├── README.md                      # Documentation index
│   ├── PROJECT_DOCUMENTATION.md       # Main project documentation
│   ├── SETUP_GUIDE.md                 # Setup instructions
│   ├── CHAT_IMPROVEMENTS.md           # Chat feature details
│   ├── CORE_REQUIREMENTS.md           # Requirements checklist
│   ├── TECHNICAL_RESOURCES_COVERAGE.md # Tech stack coverage
│   └── DEPLOYMENT_GUIDE.md            # Deployment instructions
└── README.md
```

## Error Handling

The application includes comprehensive error handling for:
- PDF extraction errors
- Vector store operations
- RAG service errors
- Content generation failures
- API validation errors

## Key Technical Highlights

- **RAG Pipeline**: Full implementation with LlamaIndex, Pinecone, and OpenAI
- **Adaptive Learning**: Q-Learning and Thompson Sampling algorithms for personalized difficulty adjustment
  - Q-Learning: Learns optimal difficulty selection based on user performance
  - Thompson Sampling: Balances exploration and exploitation for difficulty selection
  - Real-time difficulty adjustment: Increases on correct answers, decreases on incorrect
- **Systematic Prompting**: Question-type detection (7 categories) and dynamic prompt generation
- **Context Management**: Token limit handling, quality filtering, and relevance ranking
- **Session Isolation**: Namespace-based document isolation in Pinecone (each document gets unique UUID namespace)
- **Multiple File Support**: Upload and process multiple PDFs (up to 300 pages total) in a single session
- **Document Persistence**: Continue with existing documents to save API credits (LLM and Pinecone)
- **Intelligent Fallback**: Dual-layer detection system for when information is not in documents
- **Filename Preservation**: Actual filenames displayed throughout UI and in responses

## Future Enhancements

- React frontend to replace Streamlit
- User authentication and user-specific document storage
- Document management dashboard
- Caching for generated content
- Export options (PDF, DOCX, etc.)
- Multi-language support

## Documentation

All project documentation is organized in the [`project_documentation/`](project_documentation/) folder. See [project_documentation/README.md](project_documentation/README.md) for a complete index.

Key documentation files:
- **[PROJECT_DOCUMENTATION.md](project_documentation/PROJECT_DOCUMENTATION.md)** - Comprehensive project documentation
- **[SETUP_GUIDE.md](project_documentation/SETUP_GUIDE.md)** - Step-by-step setup instructions
- **[COMPLETE_VSCODE_GUIDE.md](project_documentation/COMPLETE_VSCODE_GUIDE.md)** ⭐ - **Complete VS Code guide (start here!)**
- **[VSCODE_SETUP.md](project_documentation/VSCODE_SETUP.md)** - Advanced VS Code configuration
- **[POETRY_SETUP.md](project_documentation/POETRY_SETUP.md)** - Poetry dependency management guide
- **[CHAT_IMPROVEMENTS.md](project_documentation/CHAT_IMPROVEMENTS.md)** - Chat functionality improvements
- **[CORE_REQUIREMENTS.md](project_documentation/CORE_REQUIREMENTS.md)** - Core requirements checklist
- **[TECHNICAL_RESOURCES_COVERAGE.md](project_documentation/TECHNICAL_RESOURCES_COVERAGE.md)** - Technical resources coverage
- **[DEPLOYMENT_GUIDE.md](project_documentation/DEPLOYMENT_GUIDE.md)** - Deployment instructions

## Deployment

For hosting the application, see [project_documentation/DEPLOYMENT_GUIDE.md](project_documentation/DEPLOYMENT_GUIDE.md).

For creating a portfolio website to showcase this project, see [docs/README.md](docs/README.md).

## License

This project is for educational purposes.

