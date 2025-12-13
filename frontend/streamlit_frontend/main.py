"""Streamlit main application."""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import streamlit as st

st.set_page_config(
    page_title="RAG Educational Content Generator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Main page
st.title("📚 RAG Educational Content Generator")

st.markdown(
    """
    Welcome! This application helps you interact with educational PDFs using RAG (Retrieval-Augmented Generation).

    ## Features

    - **📄 Upload PDF**: Upload and index PDF documents (up to 300 pages)
    - **💬 Chat**: Ask questions about the material
    - **📝 Generate Quiz**: Create quizzes with multiple choice and short answer questions
    - **🏆 Competitive Quiz**: Adaptive quiz with Q-Learning and Thompson Sampling
    - **📄 Generate Summary**: Get comprehensive summaries of the content
    - **🎴 Generate Flashcards**: Create flashcards for studying

    ## Getting Started

    1. Navigate to the **Upload PDF** page and upload your document
    2. Once indexed, use any of the features to interact with your material
    """
)

# Sidebar
with st.sidebar:
    st.header("Navigation")
    st.markdown(
        """
        Use the pages in the sidebar to:
        - Upload and index PDFs
        - Chat with your material
        - Generate educational content
        """
    )

    # Check backend connection
    try:
        from streamlit_frontend.utils.api_client import api_client

        health = api_client.health_check()
        st.success("✅ Backend connected")
    except Exception as e:
        st.error(f"❌ Backend connection failed: {str(e)}")
        st.info("Make sure the FastAPI backend is running on http://localhost:8000")

    # Document status
    if "document_id" in st.session_state and st.session_state.document_id:
        st.divider()
        st.success("📄 Document loaded")
        st.caption(f"ID: {st.session_state.document_id[:8]}...")

if __name__ == "__main__":
    pass

