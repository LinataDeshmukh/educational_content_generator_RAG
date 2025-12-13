"""Chat with material page."""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import streamlit as st

from streamlit_frontend.utils.api_client import api_client

st.set_page_config(page_title="Chat", page_icon="💬")

st.title("💬 Chat with Your Material")

st.markdown(
    """
    Ask questions about the uploaded PDF content. The system will use RAG to provide
    answers grounded in the document.
    """
)

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "document_id" not in st.session_state:
    st.session_state.document_id = None
if "uploaded_filename" not in st.session_state:
    st.session_state.uploaded_filename = None

# Check if document is loaded
if not st.session_state.document_id:
    st.warning("⚠️ Please upload a PDF first from the Upload page.")
    st.stop()

# Display current document info at the top
if st.session_state.uploaded_filename:
    st.info(f"📄 **Current Document:** {st.session_state.uploaded_filename}")

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        # Render markdown properly (this will render ** as bold, not show the **)
        st.markdown(message["content"], unsafe_allow_html=False)
        if "sources" in message and message["sources"]:
            with st.expander("📚 Sources"):
                for i, source in enumerate(message["sources"][:3], 1):
                    st.markdown(f"**Source {i}:**")
                    st.text(source.get("text", "")[:200] + "...")
                    if "metadata" in source:
                        st.caption(f"Page: {source['metadata'].get('page_number', 'N/A')}")

# Chat input
if prompt := st.chat_input("Ask a question about the material..."):
    # Add user message to history
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response from backend
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = api_client.chat(
                    question=prompt,
                    document_id=st.session_state.document_id,
                    filename=st.session_state.get("uploaded_filename")
                )

                answer = response.get("answer", "")
                sources = response.get("sources", [])
                from_document = response.get("from_document", True)
                message = response.get("message")
                filename = response.get("filename")

                # Show message if information is not from document
                if not from_document and message:
                    st.info(f"ℹ️ {message}")

                # Display document name if available in response
                # Always show the filename from session state or response
                display_filename = filename or st.session_state.get("uploaded_filename")
                if display_filename:
                    st.caption(f"📄 Answer based on: **{display_filename}**")

                # Render answer as markdown (this will properly render ** as bold)
                st.markdown(answer, unsafe_allow_html=False)

                if sources:
                    with st.expander("📚 Sources"):
                        for i, source in enumerate(sources[:3], 1):
                            st.markdown(f"**Source {i}:**")
                            st.text(source.get("text", "")[:200] + "...")
                            if "metadata" in source:
                                st.caption(
                                    f"Page: {source['metadata'].get('page_number', 'N/A')}"
                                )
                elif from_document:
                    # If from document but no sources shown, it's still from document
                    st.caption("Answer based on provided materials.")

                # Add assistant response to history
                st.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                    }
                )

            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": error_msg}
                )

# Sidebar controls
with st.sidebar:
    st.header("Chat Controls")
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()
    
    if st.session_state.uploaded_filename:
        st.info(f"📄 **File:** {st.session_state.uploaded_filename}")
        st.caption(f"Document ID: `{st.session_state.document_id}`")
    else:
        st.caption(f"Document ID: `{st.session_state.document_id}`")

