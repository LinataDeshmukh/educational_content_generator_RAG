"""Summary generation page."""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import streamlit as st

from streamlit_frontend.utils.api_client import api_client

st.set_page_config(page_title="Generate Summary", page_icon="📄")

st.title("📄 Generate Summary")

st.markdown(
    """
    Generate a comprehensive summary of the uploaded PDF content. Choose the length
    that best fits your needs.
    """
)

# Initialize session state
if "document_id" not in st.session_state:
    st.session_state.document_id = None
if "generated_summary" not in st.session_state:
    st.session_state.generated_summary = None

# Check if document is loaded
if not st.session_state.document_id:
    st.warning("⚠️ Please upload a PDF first from the Upload page.")
    st.stop()

# Display current document info
if st.session_state.get("uploaded_filename"):
    st.info(f"📄 **Current Document:** {st.session_state.uploaded_filename}")

# Summary configuration
with st.form("summary_config"):
    st.subheader("Summary Configuration")

    length = st.radio(
        "Summary Length",
        options=["short", "medium", "long"],
        index=1,
        help="Select the desired length of the summary",
    )

    length_descriptions = {
        "short": "2-3 paragraphs (~150-200 words)",
        "medium": "4-6 paragraphs (~300-400 words)",
        "long": "8-10 paragraphs (~600-800 words)",
    }

    st.info(f"**{length.capitalize()}:** {length_descriptions[length]}")

    submitted = st.form_submit_button("Generate Summary", type="primary")

    if submitted:
        with st.spinner("Generating summary..."):
            try:
                response = api_client.generate_summary(
                    length=length, document_id=st.session_state.document_id
                )

                st.session_state.generated_summary = response.get("summary", {})

                st.success("✅ Summary generated successfully!")

            except Exception as e:
                st.error(f"❌ Error generating summary: {str(e)}")
                st.exception(e)

# Display generated summary
if st.session_state.generated_summary:
    summary_data = st.session_state.generated_summary

    st.divider()
    st.subheader(summary_data.get("summary_title", "Document Summary"))

    summary_text = summary_data.get("summary", "")
    if summary_text:
        st.markdown(summary_text)

    # Key topics
    key_topics = summary_data.get("key_topics", [])
    if key_topics:
        st.markdown("### Key Topics")
        for topic in key_topics:
            st.markdown(f"- {topic}")

    # Word count
    word_count = summary_data.get("word_count", 0)
    if word_count:
        st.caption(f"Word count: {word_count}")

    # Download button
    import json

    summary_json = json.dumps(summary_data, indent=2)
    st.download_button(
        label="📥 Download Summary (JSON)",
        data=summary_json,
        file_name="summary.json",
        mime="application/json",
    )

    # Also allow downloading as text
    st.download_button(
        label="📥 Download Summary (TXT)",
        data=summary_text,
        file_name="summary.txt",
        mime="text/plain",
    )

# Sidebar
with st.sidebar:
    st.info(f"📄 Document ID: `{st.session_state.document_id}`")

    if st.button("Clear Summary"):
        st.session_state.generated_summary = None
        st.rerun()

