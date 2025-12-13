"""Competitive Quiz page with adaptive learning."""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import streamlit as st

from streamlit_frontend.utils.api_client import api_client

st.set_page_config(page_title="Competitive Quiz", page_icon="🏆")

st.title("🏆 Competitive Quiz")

st.markdown(
    """
    Test your knowledge with an adaptive competitive quiz! The difficulty adjusts based on your performance
    using Q-Learning and Thompson Sampling algorithms.
    
    **How it works:**
    - Generate a question bank (50 MCQ questions with low/medium/hard difficulty)
    - Start a quiz (5-10 questions)
    - Answer questions one at a time
    - Difficulty adapts based on your performance
    - Earn rewards for correct answers!
    """
)

# Initialize session state
if "document_id" not in st.session_state:
    st.session_state.document_id = None
if "competitive_quiz_bank" not in st.session_state:
    st.session_state.competitive_quiz_bank = None
if "competitive_quiz_id" not in st.session_state:
    st.session_state.competitive_quiz_id = None
if "competitive_session_id" not in st.session_state:
    st.session_state.competitive_session_id = None
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "current_difficulty" not in st.session_state:
    st.session_state.current_difficulty = None
if "quiz_stats" not in st.session_state:
    st.session_state.quiz_stats = None
if "answer_history" not in st.session_state:
    st.session_state.answer_history = []
if "show_hint" not in st.session_state:
    st.session_state.show_hint = {}
if "answer_result" not in st.session_state:
    st.session_state.answer_result = None
if "waiting_for_next" not in st.session_state:
    st.session_state.waiting_for_next = False

# Check if document is loaded
if not st.session_state.document_id:
    st.warning("⚠️ Please upload a PDF first from the Upload page.")
    st.stop()

# Display current document info
if st.session_state.get("uploaded_filename"):
    st.info(f"📄 **Current Document:** {st.session_state.uploaded_filename}")

# Check if quiz bank exists
has_existing_quiz = st.session_state.competitive_quiz_id is not None

# Main flow: Check if user wants to continue with existing quiz or generate new one
if not has_existing_quiz:
    # No existing quiz - show options to generate
    st.subheader("Generate Question Bank")
    st.markdown("Generate a question bank with 50 MCQ questions across all difficulty levels.")
    
    # Option selection: Use uploaded material or own topic
    quiz_source = st.radio(
        "Select question source:",
        ["Use Uploaded Material", "Use Own Topic"],
        key="quiz_source_selector"
    )
    
    topic = None
    if quiz_source == "Use Own Topic":
        topic = st.text_input(
            "Enter your topic:",
            placeholder="e.g., Machine Learning, Data Structures, Economics, etc.",
            help="Enter a specific topic to generate questions about",
            key="custom_topic_input"
        )
        if not topic or not topic.strip():
            st.warning("⚠️ Please enter a topic to continue.")
            st.stop()
    
    # Generate button
    if st.button("🔄 Generate Question Bank", type="primary"):
        with st.spinner("Generating question bank (50 MCQ questions)... This may take a moment."):
            try:
                response = api_client.generate_competitive_quiz_bank(
                    num_questions=50,  # Fixed at 50
                    topic=topic if topic else None,
                    document_id=st.session_state.document_id if quiz_source == "Use Uploaded Material" else None,
                )

                st.session_state.competitive_quiz_bank = response["question_bank"]
                st.session_state.competitive_quiz_id = response["quiz_id"]

                # Count questions by difficulty
                difficulty_counts = {}
                for q in response["question_bank"]:
                    diff = q.get("difficulty", "unknown")
                    difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1

                st.success("✅ Question bank generated successfully!")
                st.info(
                    f"**Total Questions:** {len(response['question_bank'])}\n\n"
                    f"**Difficulty Distribution:**\n"
                    f"- Low: {difficulty_counts.get('low', 0)}\n"
                    f"- Medium: {difficulty_counts.get('medium', 0)}\n"
                    f"- Hard: {difficulty_counts.get('hard', 0)}"
                )
                st.rerun()

            except Exception as e:
                st.error(f"❌ Error generating question bank: {str(e)}")
                st.exception(e)
else:
    # Has existing quiz - ask if they want to continue or generate new
    st.subheader("Question Bank Ready")
    st.success("✅ You have a previously generated question bank.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Generate New Question Bank", type="primary"):
            # Clear existing quiz
            st.session_state.competitive_quiz_id = None
            st.session_state.competitive_quiz_bank = None
            st.session_state.competitive_session_id = None
            st.session_state.current_question = None
            st.session_state.answer_history = []
            st.rerun()
    with col2:
        if st.button("▶️ Continue with Existing Quiz"):
            # Continue with existing - will show quiz options below
            pass

# Quiz interface (only show if quiz bank exists)
if st.session_state.competitive_quiz_id:
    st.divider()
    st.subheader("🎯 Take Competitive Quiz")
    
    if not st.session_state.competitive_session_id:
        # Quiz configuration
        num_quiz_questions = st.slider(
            "Number of Questions in Quiz",
            min_value=5,
            max_value=10,
            value=10,
            help="Select how many questions you want in this quiz",
        )
        
        # Start Quiz button at the bottom
        if st.button("▶️ Start Quiz", type="primary"):
            with st.spinner("Starting quiz..."):
                try:
                    response = api_client.start_competitive_quiz(
                        quiz_id=st.session_state.competitive_quiz_id,
                        num_questions=num_quiz_questions,
                    )

                    st.session_state.competitive_session_id = response["session_id"]
                    st.session_state.current_question = response["question"]
                    st.session_state.current_difficulty = response["current_difficulty"]
                    st.session_state.answer_history = []
                    st.session_state.quiz_stats = None
                    st.session_state.answer_result = None
                    st.session_state.waiting_for_next = False

                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error starting quiz: {str(e)}")
                    st.exception(e)
    else:
        # Quiz interface - show when quiz is active
        if st.session_state.current_question:
            question = st.session_state.current_question
            question_id = question.get("question_id")

            # Display difficulty badge
            difficulty = st.session_state.current_difficulty or question.get(
                "difficulty", "medium"
            )
            difficulty_colors = {
                "low": "🟢",
                "medium": "🟡",
                "hard": "🔴",
            }
            difficulty_labels = {
                "low": "Low",
                "medium": "Medium",
                "hard": "Hard",
            }

            # Check if we're showing result or question
            if st.session_state.waiting_for_next and st.session_state.answer_result:
                # Show result screen
                result = st.session_state.answer_result
                result_question = result.get("question", question)  # Get question from result or fallback to current
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"### Question {len(st.session_state.answer_history)} Result")
                with col2:
                    st.markdown(
                        f"**Difficulty:** {difficulty_colors.get(difficulty, '🟡')} "
                        f"{difficulty_labels.get(difficulty, 'Medium')}"
                    )

                # Display question (persist)
                st.markdown(f"**{result_question.get('question', '')}**")

                # Display options with highlighting
                options = result_question.get("options", [])
                user_answer_letter = result.get("user_answer", "").upper() if "user_answer" in result else ""
                correct_answer_letter = result.get("correct_answer", "").upper()
                
                # Find full text of user's answer and correct answer
                user_answer_text = None
                correct_answer_text = None
                
                for opt in options:
                    opt_letter = opt[0].upper() if opt else ""
                    if opt_letter == user_answer_letter:
                        user_answer_text = opt
                    if opt_letter == correct_answer_letter:
                        correct_answer_text = opt

                # Display options with visual indicators
                st.markdown("**Options:**")
                for opt in options:
                    opt_letter = opt[0].upper() if opt else ""
                    is_user_choice = opt_letter == user_answer_letter
                    is_correct = opt_letter == correct_answer_letter
                    
                    if is_correct and result["is_correct"]:
                        # User selected correct answer
                        st.success(f"✅ {opt} (Your Answer - Correct!)")
                    elif is_correct and not result["is_correct"]:
                        # Correct answer that user didn't select
                        st.success(f"✅ {opt} (Correct Answer)")
                    elif is_user_choice and not result["is_correct"]:
                        # User selected wrong answer
                        st.error(f"❌ {opt} (Your Answer - Incorrect)")
                    else:
                        # Other options
                        st.markdown(f"• {opt}")

                # Show result summary (simplified - no duplicate info)
                st.divider()
                if result["is_correct"]:
                    st.success(f"✅ **Correct!** Reward: +{result['reward']:.2f}")
                else:
                    st.error(f"❌ **Incorrect**")
                    st.caption(f"Reward: {result['reward']:.2f}")

                if result.get("explanation"):
                    with st.expander("📖 Explanation"):
                        st.markdown(result["explanation"])

                # Next button
                if result["is_complete"]:
                    st.balloons()
                    st.success("🎉 Quiz Complete!")

                    # Display final stats
                    stats = result["stats"]
                    st.markdown("### 📊 Final Statistics")

                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Accuracy", f"{stats.get('accuracy', 0):.1f}%")
                    with col2:
                        st.metric(
                            "Correct Answers",
                            f"{stats.get('correct_answers', 0)}/{stats.get('questions_answered', 0)}",
                        )
                    with col3:
                        st.metric("Total Reward", f"{stats.get('total_reward', 0):.2f}")
                    with col4:
                        st.metric(
                            "Performance Trend",
                            stats.get("performance_trend", "N/A").title(),
                        )

                    # Difficulty distribution
                    st.markdown("#### Difficulty Distribution")
                    diff_dist = stats.get("difficulty_distribution", {})
                    if diff_dist:
                        st.bar_chart(diff_dist)

                    # Answer history
                    st.markdown("#### 📝 Answer History")
                    for idx, ans in enumerate(st.session_state.answer_history, 1):
                        status = "✅" if ans["is_correct"] else "❌"
                        reward_display = f"+{ans['reward']:.2f}" if ans['reward'] > 0 else f"{ans['reward']:.2f}"
                        st.markdown(
                            f"**Q{idx}** ({ans['difficulty']}): {status} Reward: {reward_display}"
                        )

                    # Reset button
                    if st.button("Start New Quiz", type="primary"):
                        st.session_state.competitive_session_id = None
                        st.session_state.current_question = None
                        st.session_state.current_difficulty = None
                        st.session_state.answer_history = []
                        st.session_state.quiz_stats = None
                        st.session_state.answer_result = None
                        st.session_state.waiting_for_next = False
                        st.rerun()
                else:
                    # Next question button
                    if st.button("Next Question", type="primary"):
                        # Update for next question
                        st.session_state.current_question = result.get("next_question")
                        st.session_state.current_difficulty = result.get("next_difficulty")
                        st.session_state.answer_result = None
                        st.session_state.waiting_for_next = False
                        st.rerun()

            else:
                # Show question screen
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"### Question {len(st.session_state.answer_history) + 1}")
                with col2:
                    st.markdown(
                        f"**Difficulty:** {difficulty_colors.get(difficulty, '🟡')} "
                        f"{difficulty_labels.get(difficulty, 'Medium')}"
                    )

                # Display question
                st.markdown(f"**{question.get('question', '')}**")

                # Hint button
                hint = question.get("hint")
                if hint:
                    if st.button("💡 Request Hint", key=f"hint_{question_id}"):
                        st.session_state.show_hint[question_id] = True
                    
                    if st.session_state.show_hint.get(question_id, False):
                        st.info(f"💡 **Hint:** {hint}")

                # Display options
                options = question.get("options", [])
                if options:
                    selected_option = st.radio(
                        "Select your answer:",
                        options,
                        key=f"question_{question_id}",
                    )

                    # Submit button
                    if st.button("Submit Answer", type="primary"):
                        # Extract answer (A, B, C, or D)
                        answer = selected_option[0] if selected_option else ""

                        with st.spinner("Checking answer..."):
                            try:
                                response = api_client.submit_competitive_answer(
                                    session_id=st.session_state.competitive_session_id,
                                    question_id=question_id,
                                    answer=answer,
                                )

                                # Store answer in history
                                st.session_state.answer_history.append(
                                    {
                                        "question": question.get("question"),
                                        "user_answer": answer,
                                        "correct_answer": response["correct_answer"],
                                        "is_correct": response["is_correct"],
                                        "reward": response["reward"],
                                        "difficulty": difficulty,
                                    }
                                )

                                # Store result with question and user answer for display
                                result_with_question = {
                                    **response,
                                    "question": question,  # Store full question for display
                                    "user_answer": answer,  # Store user's answer letter
                                }
                                st.session_state.answer_result = result_with_question
                                st.session_state.waiting_for_next = True
                                st.session_state.quiz_stats = response["stats"]

                                st.rerun()

                            except Exception as e:
                                st.error(f"❌ Error submitting answer: {str(e)}")
                                st.exception(e)

# Sidebar
with st.sidebar:
    st.header("Competitive Quiz Info")
    st.markdown(
        """
        **Adaptive Learning:**
        - Uses Q-Learning and Thompson Sampling
        - Difficulty increases when you answer correctly
        - Difficulty decreases when you answer incorrectly
        
        **Reward System:**
        - Correct (Low): +0.50
        - Correct (Medium): +1.00
        - Correct (Hard): +1.50
        - Wrong (Low): -0.55
        - Wrong (Medium): -0.50
        - Wrong (Hard): -0.75
        
        **Difficulty Levels:**
        - 🟢 Low: Basic concepts
        - 🟡 Medium: Application of concepts
        - 🔴 Hard: Complex analysis
        """
    )

    if st.session_state.competitive_quiz_id:
        st.divider()
        st.success("✅ Question Bank Ready")
        st.caption(f"Quiz ID: {st.session_state.competitive_quiz_id[:8]}...")

    # Show current stats if available
    if st.session_state.quiz_stats:
        st.divider()
        stats = st.session_state.quiz_stats
        st.markdown("### 📊 Quiz Statistics")
        st.metric("Accuracy", f"{stats.get('accuracy', 0):.1f}%")
        st.metric(
            "Correct",
            f"{stats.get('correct_answers', 0)}/{stats.get('questions_answered', 0)}",
        )
        st.metric("Total Reward", f"{stats.get('total_reward', 0):.2f}")
        st.caption(f"Performance: {stats.get('performance_trend', 'N/A').title()}")

        # Show answer history in sidebar
        if st.session_state.answer_history:
            st.divider()
            st.markdown("### 📝 Answer History")
            for idx, ans in enumerate(st.session_state.answer_history, 1):
                status = "✅" if ans["is_correct"] else "❌"
                reward_display = (
                    f"+{ans['reward']:.2f}" if ans["reward"] > 0 else f"{ans['reward']:.2f}"
                )
                st.caption(
                    f"Q{idx} ({ans['difficulty']}): {status} Reward: {reward_display}"
                )

