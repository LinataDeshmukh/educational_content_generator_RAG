"""Flashcard generation page."""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import streamlit as st

from streamlit_frontend.utils.api_client import api_client

st.set_page_config(page_title="Generate Flashcards", page_icon="🎴")

st.title("🎴 Generate Flashcards")

st.markdown(
    """
    Generate flashcards from the uploaded PDF content. Study key concepts, definitions,
    and important information.
    """
)

# Initialize session state
if "document_id" not in st.session_state:
    st.session_state.document_id = None
if "generated_flashcards" not in st.session_state:
    st.session_state.generated_flashcards = None
if "current_card_index" not in st.session_state:
    st.session_state.current_card_index = 0
if "show_answer" not in st.session_state:
    st.session_state.show_answer = False

# Check if document is loaded
if not st.session_state.document_id:
    st.warning("⚠️ Please upload a PDF first from the Upload page.")
    st.stop()

# Display current document info
if st.session_state.get("uploaded_filename"):
    st.info(f"📄 **Current Document:** {st.session_state.uploaded_filename}")

# Flashcard configuration
with st.form("flashcard_config"):
    st.subheader("Flashcard Configuration")

    num_flashcards = st.slider(
        "Number of Flashcards",
        min_value=10,
        max_value=100,
        value=20,
        help="Select the number of flashcards to generate",
    )

    submitted = st.form_submit_button("Generate Flashcards", type="primary")

    if submitted:
        with st.spinner("Generating flashcards..."):
            try:
                response = api_client.generate_flashcards(
                    num_flashcards=num_flashcards,
                    document_id=st.session_state.document_id,
                )

                st.session_state.generated_flashcards = response.get(
                    "flashcards", {}
                )
                st.session_state.current_card_index = 0
                st.session_state.show_answer = False

                st.success("✅ Flashcards generated successfully!")

            except Exception as e:
                st.error(f"❌ Error generating flashcards: {str(e)}")
                st.exception(e)

# Display flashcards
if st.session_state.generated_flashcards:
    flashcards_data = st.session_state.generated_flashcards
    flashcards_list = flashcards_data.get("flashcards", [])

    if flashcards_list:
        st.divider()
        st.subheader(flashcards_data.get("flashcard_set_title", "Flashcards"))

        total_cards = len(flashcards_list)
        current_index = st.session_state.current_card_index

        # Card navigation
        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            if st.button("◀ Previous", disabled=current_index == 0):
                st.session_state.current_card_index = max(0, current_index - 1)
                st.session_state.show_answer = False
                st.rerun()

        with col2:
            st.markdown(
                f"<div style='text-align: center;'><b>Card {current_index + 1} of {total_cards}</b></div>",
                unsafe_allow_html=True,
            )

        with col3:
            if st.button("Next ▶", disabled=current_index >= total_cards - 1):
                st.session_state.current_card_index = min(
                    total_cards - 1, current_index + 1
                )
                st.session_state.show_answer = False
                st.rerun()

        # Display current card
        current_card = flashcards_list[current_index]

        # Card display
        card_container = st.container()
        with card_container:
            st.markdown("---")
            st.markdown(
                f"""
                <div style='border: 2px solid #1f77b4; border-radius: 10px; padding: 20px; 
                           text-align: center; min-height: 200px; display: flex; 
                           align-items: center; justify-content: center;'>
                    <div>
                        <h3>{current_card.get('front', '')}</h3>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("---")

        # Show/Hide answer button
        if st.button(
            "Show Answer" if not st.session_state.show_answer else "Hide Answer"
        ):
            st.session_state.show_answer = not st.session_state.show_answer

        # Display answer
        if st.session_state.show_answer:
            with st.container():
                st.markdown(
                    f"""
                    <div style='border: 2px solid #2ca02c; border-radius: 10px; padding: 20px; 
                               background-color: #f0f9f0;'>
                        <h4 style='color: #000000;'>Answer:</h4>
                        <p style='color: #000000;'>{current_card.get('back', '')}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Category if available
                category = current_card.get("category")
                if category:
                    st.caption(f"Category: {category}")

        # Download button
        import json

        flashcards_json = json.dumps(flashcards_data, indent=2)
        st.download_button(
            label="📥 Download Flashcards (JSON)",
            data=flashcards_json,
            file_name="flashcards.json",
            mime="application/json",
        )

# Sidebar
with st.sidebar:
    st.info(f"📄 Document ID: `{st.session_state.document_id}`")

    if st.button("Clear Flashcards"):
        st.session_state.generated_flashcards = None
        st.session_state.current_card_index = 0
        st.session_state.show_answer = False
        st.rerun()

