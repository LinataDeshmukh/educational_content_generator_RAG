# Learnify - RAG-Powered Educational Content Generator

A comprehensive application that uses RAG (Retrieval-Augmented Generation) to help students and educators interact with PDF educational materials. Upload a PDF, and the system enables you to chat with the material, generate quizzes with detailed analytics, summaries, and flashcards.

## Features

- **PDF Processing**: Upload and index multiple PDF documents (up to 300 pages total)
- **Auto-Index Creation**: Pinecone index is automatically created if it doesn't exist
- **Document Persistence**: Continue with previously uploaded documents to save API credits
- **Chat Interface**: Ask questions about the material with RAG-powered answers and intelligent fallback
- **Quiz Generation**: Generate contextual quizzes with detailed statistical analysis and visual performance charts
- **Competitive Quiz**: Adaptive difficulty quiz system (30 questions) using Q-Learning and Thompson Sampling algorithms with comprehensive statistics
- **Summary Generation**: Create comprehensive summaries (short, medium, or long)
- **Flashcard Generation**: Generate flashcards for studying key concepts
- **Visual Analytics**: Interactive charts and graphs for quiz performance analysis

## Architecture

The project consists of:

- **Backend** (`backend/`): FastAPI application with RAG pipeline
- **Frontend** (`frontend_v2/`): Next.js React application (recommended)
- **Frontend (Legacy)** (`frontend/`): Streamlit UI application

## Tech Stack

### Backend
- **FastAPI** - REST API framework
- **LlamaIndex** - RAG orchestration
- **Pinecone** - Vector database (with namespace isolation and auto-creation)
- **PyMuPDF** - PDF text extraction
- **OpenAI** - Embeddings and LLM
- **NumPy** - Adaptive learning algorithms
- **Poetry** - Dependency management

### Frontend (Next.js)
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Zustand** - State management
- **Lucide React** - Icons

### Frontend (Streamlit - Legacy)
- **Streamlit** - Web UI framework
- **httpx** - HTTP client for API communication
- **Matplotlib & Pandas** - Data visualization

## Quick Start

### Prerequisites

- Python 3.9+
- Poetry (https://python-poetry.org/docs/#installation)
- Node.js 18+ and npm (for Next.js frontend)
- OpenAI API key
- Pinecone API key

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

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

5. Run the backend server:
```bash
poetry run backend
```

The API will be available at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`.

### Frontend Setup (Next.js - Recommended)

1. Navigate to the frontend directory:
```bash
cd frontend_v2
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env.local` file:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Run the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`.

### Frontend Setup (Streamlit - Legacy)

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
poetry install
```

3. Create `.env` file:
```env
BACKEND_API_URL=http://localhost:8000
```

4. Run the Streamlit app:
```bash
poetry run frontend
```

The app will be available at `http://localhost:8501`.

## Usage

1. **Upload PDF(s)**: Go to the Upload page and upload one or multiple PDF documents (up to 300 pages total)
   - Option to continue with previously uploaded documents
   - Document names are displayed throughout the application

2. **Chat**: Use the Chat page to ask questions about the material with intelligent RAG responses

3. **Generate Quiz**: Create contextual quizzes with:
   - Multiple choice and short answer questions
   - Detailed statistical analysis with visual charts
   - Performance breakdown by question type
   - Answer history visualization

4. **Competitive Quiz**: Experience adaptive difficulty quizzes (30 questions) that adjust based on your performance:
   - Q-Learning and Thompson Sampling algorithms
   - Real-time statistics with progress bars
   - Comprehensive final statistics with visual charts
   - Difficulty distribution analysis
   - Reward tracking

5. **Generate Summary**: Get summaries of varying lengths (short, medium, long)

6. **Generate Flashcards**: Create flashcards for studying key concepts

## Project Structure

```
educational_content_generator_RAG/
├── backend/
│   ├── fastapi_backend/          # Main backend package
│   │   ├── __main__.py           # Entry point
│   │   ├── main.py               # FastAPI app
│   │   ├── config.py             # Configuration
│   │   ├── dependencies.py       # Dependency injection
│   │   ├── middleware.py         # Exception handling
│   │   ├── models/               # Data models (Pydantic schemas)
│   │   ├── routers/              # API routes
│   │   │   ├── upload.py
│   │   │   ├── chat.py
│   │   │   ├── quiz.py
│   │   │   ├── competitive_quiz.py
│   │   │   ├── summary.py
│   │   │   ├── flashcards.py
│   │   │   └── documents.py
│   │   ├── services/             # Business logic
│   │   │   ├── rag_service.py
│   │   │   ├── vector_store.py  # Pinecone with auto-creation
│   │   │   ├── content_generator.py
│   │   │   ├── competitive_quiz_service.py
│   │   │   └── pdf_extractor.py
│   │   └── utils/                # Utilities
│   │       ├── chunking.py
│   │       ├── adaptive_learning.py
│   │       └── errors.py
│   └── pyproject.toml
├── frontend_v2/                  # Next.js frontend (recommended)
│   ├── app/                      # Next.js app directory
│   │   ├── page.tsx              # Home page
│   │   ├── upload/               # Upload page
│   │   ├── chat/                 # Chat page
│   │   ├── quiz/                 # Quiz page with statistics
│   │   ├── competitive-quiz/    # Competitive quiz with analytics
│   │   ├── summary/              # Summary page
│   │   └── flashcards/           # Flashcards page
│   ├── components/               # React components
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   └── ThemeProvider.tsx
│   ├── lib/                      # Utilities
│   │   ├── api.ts                # API client
│   │   └── store.ts              # Zustand store
│   └── package.json
├── frontend/                     # Streamlit frontend (legacy)
│   └── streamlit_frontend/
├── docs/                         # GitHub Pages website
├── project_documentation/         # Project documentation
├── RUN.md                        # Quick run instructions
├── SETUP_STEPS.md                # Detailed setup guide
└── README.md                     # This file
```

## Key Features & Improvements

### Statistical Analysis
- **Quiz Statistics**: Comprehensive performance analysis with:
  - Overall score, completion rate, and accuracy metrics
  - Breakdown by question type (Multiple Choice vs Short Answer)
  - Visual progress bars and bar charts
  - Answer history with visual grid representation

- **Competitive Quiz Statistics**: Advanced analytics including:
  - Real-time performance tracking with progress bars
  - Final statistics with visual charts
  - Difficulty distribution analysis (Low/Medium/Hard)
  - Reward tracking and performance trends
  - Visual answer history grid

### Technical Highlights

- **RAG Pipeline**: Full implementation with LlamaIndex, Pinecone, and OpenAI
- **Pinecone Auto-Creation**: Index is automatically created if it doesn't exist
- **Adaptive Learning**: Q-Learning and Thompson Sampling algorithms for personalized difficulty adjustment
  - Q-Learning: Learns optimal difficulty selection based on user performance
  - Thompson Sampling: Balances exploration and exploitation for difficulty selection
  - Real-time difficulty adjustment: Increases on correct answers, decreases on incorrect
- **Systematic Prompting**: Question-type detection and dynamic prompt generation
- **Context Management**: Token limit handling, quality filtering, and relevance ranking
- **Session Isolation**: Namespace-based document isolation in Pinecone (each document gets unique UUID namespace)
- **Multiple File Support**: Upload and process multiple PDFs (up to 300 pages total) in a single session
- **Document Persistence**: Continue with existing documents to save API credits
- **Intelligent Fallback**: Dual-layer detection system for when information is not in documents
- **Filename Preservation**: Actual filenames displayed throughout UI and in responses
- **Modern UI**: Clean, minimal design with light/dark mode support

## Error Handling

The application includes comprehensive error handling for:
- PDF extraction errors
- Vector store operations (with auto-creation fallback)
- RAG service errors
- Content generation failures
- API validation errors

## Documentation

- **[RUN.md](RUN.md)** - Quick start guide for running the application
- **[SETUP_STEPS.md](SETUP_STEPS.md)** - Detailed setup instructions including NLTK data
- **[project_documentation/](project_documentation/)** - Comprehensive project documentation

## Deployment

For hosting the application, see [project_documentation/DEPLOYMENT_GUIDE.md](project_documentation/DEPLOYMENT_GUIDE.md).

For creating a portfolio website to showcase this project, see [docs/README.md](docs/README.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2024 Linata Deshmukh & Pranesh Kannan
