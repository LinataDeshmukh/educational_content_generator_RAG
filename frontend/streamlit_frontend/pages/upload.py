"""PDF upload page."""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import logging
import streamlit as st

from streamlit_frontend.utils.api_client import api_client

logger = logging.getLogger(__name__)

st.set_page_config(page_title="Upload PDF", page_icon="📄")

st.title("📄 Upload PDF")

st.markdown(
    """
    Upload one or more PDF documents (up to 300 pages total) to extract and index their content.
    Once uploaded, you can chat with the material, generate quizzes, summaries, and flashcards.
    
    **Note:** Only PDF files are accepted. The total page count across all files must not exceed 300 pages.
    """
)

# Initialize session state
if "document_id" not in st.session_state:
    st.session_state.document_id = None
if "uploaded_filename" not in st.session_state:
    st.session_state.uploaded_filename = None
if "checked_existing_docs" not in st.session_state:
    st.session_state.checked_existing_docs = False
if "existing_documents" not in st.session_state:
    st.session_state.existing_documents = []
if "document_loaded_from_existing" not in st.session_state:
    st.session_state.document_loaded_from_existing = False

# Check for existing documents on page load (only once)
if not st.session_state.checked_existing_docs and not st.session_state.document_id:
    with st.spinner("Checking for existing documents..."):
        try:
            response = api_client.list_documents()
            existing_docs = response.get("documents", [])
            st.session_state.existing_documents = existing_docs
            st.session_state.checked_existing_docs = True
            
            if existing_docs:
                st.info("ℹ️ Found existing documents in Pinecone. You can continue with an existing document or upload a new one.")
        except Exception as e:
            logger.warning(f"Could not check for existing documents: {e}")
            st.session_state.checked_existing_docs = True

# Show existing documents option if available
if st.session_state.existing_documents and not st.session_state.document_id:
    st.markdown("### 📚 Continue with Existing Document")
    st.markdown("Select a previously uploaded document to continue working with it (saves credits!):")
    
    # Create a selectbox with existing documents
    doc_options = [
        f"{doc.get('filename', 'Unknown')} ({doc.get('vector_count', 0)} vectors)"
        for doc in st.session_state.existing_documents
    ]
    doc_options.insert(0, "--- Upload New Document ---")
    
    selected_doc = st.selectbox(
        "Choose an option:",
        doc_options,
        key="existing_doc_selector"
    )
    
    if selected_doc and selected_doc != "--- Upload New Document ---":
        # User selected an existing document
        selected_index = doc_options.index(selected_doc) - 1  # -1 because we added "Upload New" at index 0
        selected_document = st.session_state.existing_documents[selected_index]
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Continue with This Document", type="primary"):
                st.session_state.document_id = selected_document["document_id"]
                filename = selected_document.get("filename", "Unknown")
                # Clean up filename if it shows "Document ..." pattern
                if filename.startswith("Document ") and "..." in filename:
                    filename = f"Document {selected_document['document_id'][:8]}..."
                st.session_state.uploaded_filename = filename
                st.session_state.document_loaded_from_existing = True
                # Clear chat history when loading existing document
                if "chat_history" in st.session_state:
                    st.session_state.chat_history = []
                # Clear competitive quiz state
                if "competitive_quiz_id" in st.session_state:
                    st.session_state.competitive_quiz_id = None
                    st.session_state.competitive_quiz_bank = None
                # Clear auto-generated flag for competitive quiz
                if "auto_generated" in st.session_state:
                    st.session_state.auto_generated = False
                st.success(f"✅ Loaded document: {filename}")
                st.rerun()
        with col2:
            if st.button("🗑️ Delete This Document"):
                # TODO: Add delete endpoint if needed
                st.warning("Delete functionality coming soon. For now, documents persist in Pinecone.")
        
        st.info(
            f"**Document ID:** `{selected_document['document_id']}`\n\n"
            f"**Filename:** {selected_document.get('filename', 'Unknown')}\n\n"
            f"**Vectors:** {selected_document.get('vector_count', 0)}"
        )
    
    st.divider()
    st.markdown("### 📤 Or Upload New Document")

# File uploader - allow multiple files
uploaded_files = st.file_uploader(
    "Choose PDF file(s)",
    type=["pdf"],
    accept_multiple_files=True,
    help="Upload one or more PDF files (up to 300 pages total). Only PDF files are accepted.",
)

if uploaded_files and len(uploaded_files) > 0:
    # Display selected files
    st.info(f"Selected {len(uploaded_files)} file(s):")
    for file in uploaded_files:
        st.write(f"  - {file.name} ({file.size / 1024:.1f} KB)")

    if st.button("Upload and Index", type="primary"):
        with st.spinner(f"Uploading and processing {len(uploaded_files)} PDF file(s)..."):
            try:
                # Validate file types
                invalid_files = [f.name for f in uploaded_files if not f.name.lower().endswith('.pdf')]
                if invalid_files:
                    st.error(f"❌ Only PDF files are allowed. Invalid files: {', '.join(invalid_files)}")
                else:
                    # Read all file bytes and store actual file names
                    files_data = []
                    actual_file_names = []
                    for file in uploaded_files:
                        file.seek(0)  # Reset file pointer
                        files_data.append((file.read(), file.name))
                        actual_file_names.append(file.name)

                    # Upload to backend (multiple files)
                    response = api_client.upload_pdf_multiple(files_data)

                    # Store document ID and filename in session state
                    st.session_state.document_id = response["document_id"]
                    # Always use actual file names from uploaded files
                    # Use filename from response if it contains actual names, otherwise use uploaded file names
                    filename_from_response = response.get("filename", "")
                    if filename_from_response and filename_from_response != f"{len(uploaded_files)} files":
                        # Response has actual file names
                        filename = filename_from_response
                    else:
                        # Use actual file names from uploaded files
                        filename = ", ".join(actual_file_names)
                    st.session_state.uploaded_filename = filename
                    
                    # Clear chat history when new document is uploaded (session isolation)
                    if "chat_history" in st.session_state:
                        st.session_state.chat_history = []

                    st.success(f"✅ {len(uploaded_files)} PDF file(s) uploaded and indexed successfully!")
                    
                    # Display upload details with actual file names
                    file_list = ", ".join([f.name for f in uploaded_files])
                    st.info(
                        f"📚 Document ID: `{response['document_id']}`\n\n"
                        f"📄 Files: {file_list}\n\n"
                        f"📄 Total Pages: {response['page_count']}\n\n"
                        f"🔢 Chunks created: {response['chunks_created']}"
                    )

            except Exception as e:
                error_msg = str(e)
                # Try to extract the actual error detail from the response
                actual_error = error_msg
                if hasattr(e, 'response') and e.response is not None:
                    try:
                        error_detail = e.response.json()
                        if 'detail' in error_detail:
                            actual_error = error_detail['detail']
                    except:
                        pass
                
                if "exceeds the maximum limit" in actual_error or "300" in actual_error:
                    st.error(f"❌ {actual_error}")
                    st.warning("💡 Please upload files with fewer total pages (maximum 300 pages combined).")
                elif "Only PDF files" in actual_error or ("PDF" in actual_error and "allowed" in actual_error):
                    st.error(f"❌ {actual_error}")
                    st.warning("💡 Please ensure all files are PDF format (.pdf extension).")
                else:
                    st.error(f"❌ Error uploading PDF(s): {actual_error}")
                    if "400" in error_msg:
                        st.warning("💡 This might be a file format issue. Please ensure all files are valid PDFs.")
                    st.exception(e)

# Display current document info
if st.session_state.document_id:
    st.sidebar.success("✅ Document loaded")
    st.sidebar.info(f"📄 File: {st.session_state.uploaded_filename}")
    st.sidebar.info(f"🆔 ID: {st.session_state.document_id}")

    if st.sidebar.button("Clear Document"):
        st.session_state.document_id = None
        st.session_state.uploaded_filename = None
        st.rerun()

