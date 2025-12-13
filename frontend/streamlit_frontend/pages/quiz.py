"""Quiz generation page."""

import sys
from pathlib import Path


# Add src to Python path
src_path = Path(__file__).parent.parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from streamlit_frontend.utils.api_client import api_client

st.set_page_config(page_title="Generate Quiz", page_icon="📝")

st.title("📝 Generate Quiz")

st.markdown(
    """
    Generate a quiz from the uploaded PDF content. You can customize the number of
    questions and question types.
    """
)

# Initialize session state
if "document_id" not in st.session_state:
    st.session_state.document_id = None
if "generated_quiz" not in st.session_state:
    st.session_state.generated_quiz = None
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}
if "show_results" not in st.session_state:
    st.session_state.show_results = False

# Check if document is loaded
if not st.session_state.document_id:
    st.warning("⚠️ Please upload a PDF first from the Upload page.")
    st.stop()

# Display current document info
if st.session_state.get("uploaded_filename"):
    st.info(f"📄 **Current Document:** {st.session_state.uploaded_filename}")

# Quiz configuration
with st.form("quiz_config"):
    st.subheader("Quiz Configuration")

    num_questions = st.slider(
        "Number of Questions",
        min_value=5,
        max_value=50,
        value=10,
        help="Select the number of questions to generate",
    )

    question_types = st.multiselect(
        "Question Types",
        options=["multiple_choice", "short_answer"],
        default=["multiple_choice", "short_answer"],
        help="Select the types of questions to include",
    )

    submitted = st.form_submit_button("Generate Quiz", type="primary")

    if submitted:
        if not question_types:
            st.error("Please select at least one question type.")
        else:
            with st.spinner("Generating quiz..."):
                try:
                    response = api_client.generate_quiz(
                        num_questions=num_questions,
                        question_types=question_types,
                        document_id=st.session_state.document_id,
                    )

                    st.session_state.generated_quiz = response.get("quiz", {})
                    st.session_state.quiz_answers = {}  # Reset answers
                    st.session_state.show_results = False  # Reset results

                    st.success("✅ Quiz generated successfully!")

                except Exception as e:
                    st.error(f"❌ Error generating quiz: {str(e)}")
                    st.exception(e)

# Display generated quiz
if st.session_state.generated_quiz:
    quiz_data = st.session_state.generated_quiz

    st.divider()
    st.subheader(quiz_data.get("quiz_title", "Generated Quiz"))

    questions = quiz_data.get("questions", [])

    if questions:
        if st.session_state.show_results:
            st.success("✅ Quiz submitted! View your performance report below.")
            st.markdown("---")
        
        st.divider()
        
        # Display questions with answer inputs
        for i, question in enumerate(questions, 1):
            with st.container():
                st.markdown(f"### Question {i}")
                
                question_key = f"q_{i}"
                question_type = question.get("question_type", "")
                correct_answer = question.get("correct_answer", "")
                
                if question_type == "multiple_choice":
                    # Display question with context
                    st.markdown(f"**{question.get('question', '')}**")
                    
                    options = question.get("options", [])
                    if not options:
                        st.warning("⚠️ No options available for this question")
                    else:
                        # Parse options - handle both "A) Option text" and just "Option text" formats
                        option_display = []
                        for opt in options:
                            if ") " in opt:
                                # Format: "A) Option text"
                                option_display.append(opt)
                            else:
                                # Format: just "Option text" - add label
                                idx = options.index(opt)
                                label = chr(65 + idx)  # A, B, C, D
                                option_display.append(f"{label}) {opt}")
                        
                        # Radio buttons for answer selection
                        if not st.session_state.show_results:
                            current_answer_idx = st.session_state.quiz_answers.get(question_key)
                            selected_option = st.radio(
                                "Select your answer:",
                                options=option_display,
                                key=question_key,
                                index=current_answer_idx if current_answer_idx is not None else None,
                            )
                            if selected_option:
                                st.session_state.quiz_answers[question_key] = option_display.index(selected_option)
                            
                            # Hint button (available during quiz)
                            hint = question.get("hint", "Think about the key concepts mentioned in the question context.")
                            with st.expander("💡 Hint", expanded=False):
                                st.info(f"**Hint:** {hint}")
                        else:
                            # After submission - show answers in consistent format
                            # Keep options visible
                            st.markdown("**Options:**")
                            for opt in option_display:
                                st.markdown(f"- {opt}")
                            
                            user_answer_idx = st.session_state.quiz_answers.get(question_key)
                            
                            # Find correct answer option
                            correct_option = next((opt for opt in option_display if opt.startswith(correct_answer)), None)
                            if not correct_option:
                                correct_option = correct_answer
                            
                            # Show user's answer
                            if user_answer_idx is not None:
                                user_selected = option_display[user_answer_idx]
                                # Extract label from user's answer
                                user_label = user_selected.split(")")[0] + ")" if ") " in user_selected else user_selected
                                is_correct = user_label == correct_answer or user_selected.startswith(correct_answer)
                                
                                # Show user's answer
                                st.markdown("**Your Answer:**")
                                if is_correct:
                                    st.success(f"✅ {user_selected}")
                                else:
                                    st.error(f"❌ {user_selected}")
                                    # Only show correct answer if wrong
                                    st.markdown("**Correct Answer:**")
                                    st.success(f"✅ {correct_option}")
                            else:
                                # User didn't answer
                                st.markdown("**Your Answer:**")
                                st.warning("⚠️ You didn't answer this question")
                                
                                # Show correct answer
                                st.markdown("**Correct Answer:**")
                                st.success(f"✅ {correct_option}")
                            
                            # Show explanation
                            if question.get("explanation"):
                                st.markdown("**Explanation:**")
                                st.info(question.get("explanation"))

                elif question_type == "short_answer":
                    # Display question with context
                    st.markdown(f"**{question.get('question', '')}**")
                    
                    # Text input for short answer
                    if not st.session_state.show_results:
                        user_answer = st.text_area(
                            "Enter your answer:",
                            key=question_key,
                            value=st.session_state.quiz_answers.get(question_key, ""),
                            height=100,
                        )
                        st.session_state.quiz_answers[question_key] = user_answer
                        
                        # Hint button
                        hint = question.get("hint", "Consider the main concepts and context provided in the question.")
                        with st.expander("💡 Hint", expanded=False):
                            st.info(f"**Hint:** {hint}")
                    else:
                        # After submission - show answers in consistent format
                        user_answer = st.session_state.quiz_answers.get(question_key, "").strip()
                        
                        # Show user's answer
                        st.markdown("**Your Answer:**")
                        if user_answer:
                            # Evaluate answer using LLM
                            eval_key = f"eval_{question_key}"
                            if eval_key not in st.session_state:
                                with st.spinner("Evaluating your answer..."):
                                    try:
                                        evaluation = api_client.evaluate_answer(
                                            user_answer=user_answer,
                                            correct_answer=correct_answer,
                                            question=question.get('question', ''),
                                        )
                                        st.session_state[eval_key] = evaluation
                                    except Exception as e:
                                        st.error(f"Error evaluating answer: {str(e)}")
                                        st.session_state[eval_key] = {"is_correct": False, "feedback": "Evaluation failed"}
                            
                            evaluation = st.session_state.get(eval_key, {})
                            is_correct = evaluation.get("is_correct", False)
                            
                            if is_correct:
                                st.success(f"✅ {user_answer}")
                            else:
                                st.error(f"❌ {user_answer}")
                                # Only show correct answer if wrong
                                st.markdown("**Correct Answer:**")
                                st.success(f"✅ {correct_answer}")
                            
                            # Show feedback if available
                            feedback = evaluation.get("feedback", "")
                            if feedback:
                                st.info(f"💡 {feedback}")
                        else:
                            st.warning("⚠️ You didn't answer this question")
                            # Show correct answer
                            st.markdown("**Correct Answer:**")
                            st.success(f"✅ {correct_answer}")
                        
                        # Show explanation
                        if question.get("explanation"):
                            st.markdown("**Explanation:**")
                            st.info(question.get("explanation"))

                st.divider()
        
        # Submit button at the bottom (after all questions)
        if not st.session_state.show_results:
            st.markdown("---")
            st.markdown("### Ready to Submit?")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("📤 Submit Quiz", type="primary", use_container_width=True, key="submit_quiz_bottom"):
                    # Check if at least one question is answered
                    answered_count_check = 0
                    for i in range(1, len(questions) + 1):
                        question_key = f"q_{i}"
                        question = questions[i-1]
                        if question.get('question_type') == 'multiple_choice':
                            if st.session_state.quiz_answers.get(question_key) is not None:
                                answered_count_check += 1
                        elif question.get('question_type') == 'short_answer':
                            if st.session_state.quiz_answers.get(question_key, "").strip():
                                answered_count_check += 1
                    
                    if answered_count_check == 0:
                        st.warning("⚠️ Please answer at least one question before submitting.")
                    else:
                        st.session_state.show_results = True
                        st.rerun()
            st.markdown("---")
        
        # Show score if results are displayed
        if st.session_state.show_results:
            total_questions = len(questions)
            correct_count = 0
            answered_count = 0
            
            for i, question in enumerate(questions, 1):
                question_key = f"q_{i}"
                question_type = question.get("question_type", "")
                correct_answer = question.get("correct_answer", "")
                
                if question_type == "multiple_choice":
                    user_answer_idx = st.session_state.quiz_answers.get(question_key)
                    if user_answer_idx is not None:
                        answered_count += 1
                        options = question.get("options", [])
                        # Parse options to get labels
                        option_labels = []
                        for opt in options:
                            if ") " in opt:
                                option_labels.append(opt.split(")")[0] + ")")
                            else:
                                idx = options.index(opt)
                                option_labels.append(chr(65 + idx) + ")")
                        
                        if user_answer_idx < len(option_labels):
                            user_selected = option_labels[user_answer_idx]
                            # Check if correct (handle both "A)" and "A) Option text" formats)
                            if user_selected == correct_answer or correct_answer.startswith(user_selected.replace(")", "")):
                                correct_count += 1
                elif question_type == "short_answer":
                    user_answer = st.session_state.quiz_answers.get(question_key, "").strip()
                    if user_answer:
                        answered_count += 1
                        # Check evaluation result for short answers
                        eval_key = f"eval_{question_key}"
                        evaluation = st.session_state.get(eval_key, {})
                        if evaluation.get("is_correct", False):
                            correct_count += 1
            
            st.markdown("---")
            st.markdown("## 📊 Statistical Performance Report")
            st.markdown("### Overall Performance Summary")
            
            # Calculate comprehensive statistics
            mc_questions = [q for q in questions if q.get('question_type') == 'multiple_choice']
            sa_questions = [q for q in questions if q.get('question_type') == 'short_answer']
            mc_total = len(mc_questions)
            sa_total = len(sa_questions)
            
            # Calculate MC stats
            mc_answered = sum(1 for i, q in enumerate(questions, 1) 
                             if q.get('question_type') == 'multiple_choice' 
                             and st.session_state.quiz_answers.get(f"q_{i}") is not None)
            mc_correct = 0
            for i, q in enumerate(questions, 1):
                if q.get('question_type') == 'multiple_choice':
                    user_idx = st.session_state.quiz_answers.get(f"q_{i}")
                    if user_idx is not None:
                        options = q.get("options", [])
                        option_labels = []
                        for opt in options:
                            if ") " in opt:
                                option_labels.append(opt.split(")")[0] + ")")
                            else:
                                idx = options.index(opt)
                                option_labels.append(chr(65 + idx) + ")")
                        if user_idx < len(option_labels):
                            user_selected = option_labels[user_idx]
                            correct_ans = q.get("correct_answer", "")
                            if user_selected == correct_ans or correct_ans.startswith(user_selected.replace(")", "")):
                                mc_correct += 1
            
            # Calculate SA stats
            sa_answered = sum(1 for i, q in enumerate(questions, 1) 
                            if q.get('question_type') == 'short_answer' 
                            and st.session_state.quiz_answers.get(f"q_{i}", "").strip())
            sa_correct = sum(1 for i, q in enumerate(questions, 1)
                            if q.get('question_type') == 'short_answer'
                            and st.session_state.quiz_answers.get(f"q_{i}", "").strip()
                            and st.session_state.get(f"eval_q_{i}", {}).get("is_correct", False))
            
            mc_incorrect = mc_answered - mc_correct
            mc_unanswered = mc_total - mc_answered
            mc_percentage = (mc_correct / mc_total * 100) if mc_total > 0 else 0
            
            # Overall score includes both MC and SA
            total_correct = mc_correct + sa_correct
            overall_percentage = (total_correct / total_questions * 100) if total_questions > 0 else 0
            
            sa_total = len(sa_questions)
            sa_answered = sum(1 for i, q in enumerate(questions, 1) 
                            if q.get('question_type') == 'short_answer' 
                            and st.session_state.quiz_answers.get(f"q_{i}", "").strip())
            sa_unanswered = sa_total - sa_answered
            
            completion_rate = (answered_count / total_questions * 100) if total_questions > 0 else 0
            accuracy_rate = (mc_correct / mc_answered * 100) if mc_answered > 0 else 0
            
            # Key Metrics Dashboard
            st.markdown("#### Key Performance Indicators")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Questions", total_questions, help="Total number of questions in the quiz")
            with col2:
                st.metric("Completion Rate", f"{completion_rate:.1f}%", 
                         delta=f"{answered_count}/{total_questions} answered",
                         delta_color="normal" if completion_rate >= 80 else "off",
                         help="Percentage of questions answered")
            with col3:
                st.metric("Accuracy Rate", f"{accuracy_rate:.1f}%",
                         delta=f"{mc_correct}/{mc_answered} correct",
                         delta_color="normal" if accuracy_rate >= 70 else "off",
                         help="Percentage of correct answers (Multiple Choice only)")
            with col4:
                st.metric("Overall Score", f"{overall_percentage:.1f}%",
                         delta=f"{total_correct}/{total_questions} correct",
                         delta_color="normal" if overall_percentage >= 70 else "off",
                         help="Overall performance score (MC + SA)")
            
            # Visualizations
            # Chart 1: Performance by Question Type
            if mc_total > 0 or len(sa_questions) > 0:
                fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
                
                # Pie chart for question type distribution
                type_labels = []
                type_sizes = []
                if mc_total > 0:
                    type_labels.append("Multiple Choice")
                    type_sizes.append(mc_total)
                if len(sa_questions) > 0:
                    type_labels.append("Short Answer")
                    type_sizes.append(len(sa_questions))
                
                if type_labels:
                    colors1 = ['#1f77b4', '#2ca02c']
                    ax1.pie(type_sizes, labels=type_labels, autopct='%1.1f%%', colors=colors1[:len(type_labels)], startangle=90)
                    ax1.set_title("Question Type Distribution")
                
                # Bar chart for multiple choice performance
                if mc_total > 0:
                    categories = ['Correct', 'Incorrect', 'Unanswered']
                    mc_answered = sum(1 for i, q in enumerate(questions, 1) 
                                     if q.get('question_type') == 'multiple_choice' 
                                     and st.session_state.quiz_answers.get(f"q_{i}") is not None)
                    mc_incorrect = mc_answered - mc_correct
                    mc_unanswered = mc_total - mc_answered
                    values = [mc_correct, mc_incorrect, mc_unanswered]
                    colors2 = ['#2ca02c', '#d62728', '#ff7f0e']
                    bars = ax2.bar(categories, values, color=colors2)
                    ax2.set_title("Multiple Choice Performance")
                    ax2.set_ylabel("Number of Questions")
                    ax2.set_ylim(0, max(values) * 1.2 if max(values) > 0 else 1)
                    
                    # Add value labels on bars
                    for bar in bars:
                        height = bar.get_height()
                        if height > 0:
                            ax2.text(bar.get_x() + bar.get_width()/2., height,
                                   f'{int(height)}',
                                   ha='center', va='bottom')
                
                plt.tight_layout()
                st.pyplot(fig1)
            
            # Chart 2: Performance Score Visualization
            fig2, ax3 = plt.subplots(figsize=(10, 6))
            
            # Create a gauge/score visualization
            score_percentage = mc_percentage
            categories_perf = ['Excellent\n(90-100%)', 'Good\n(70-89%)', 'Fair\n(50-69%)', 'Needs Improvement\n(<50%)']
            if score_percentage >= 90:
                perf_level = 0
                perf_color = '#2ca02c'
            elif score_percentage >= 70:
                perf_level = 1
                perf_color = '#1f77b4'
            elif score_percentage >= 50:
                perf_level = 2
                perf_color = '#ff7f0e'
            else:
                perf_level = 3
                perf_color = '#d62728'
            
            # Bar chart showing performance level
            perf_values = [0, 0, 0, 0]
            perf_values[perf_level] = score_percentage
            bars = ax3.barh(categories_perf, perf_values, color=perf_color, alpha=0.7)
            ax3.set_xlim(0, 100)
            ax3.set_xlabel("Score Percentage")
            ax3.set_title(f"Performance Level: {score_percentage:.1f}%")
            ax3.axvline(x=score_percentage, color=perf_color, linestyle='--', linewidth=2, label=f'Your Score: {score_percentage:.1f}%')
            ax3.legend()
            
            # Add score text
            ax3.text(score_percentage, perf_level, f'{score_percentage:.1f}%', 
                    ha='center', va='center', fontsize=14, fontweight='bold', color='white')
            
            plt.tight_layout()
            st.pyplot(fig2)
            
            # Detailed Statistical Breakdown
            st.markdown("---")
            st.markdown("#### 📈 Detailed Statistical Analysis")
            
            breakdown_col1, breakdown_col2 = st.columns(2)
            
            with breakdown_col1:
                st.markdown("**Multiple Choice Questions Analysis**")
                if mc_total > 0:
                    # Progress bar for MC
                    st.progress(mc_percentage / 100, text=f"Score: {mc_percentage:.1f}%")
                    
                    st.markdown(f"""
                    - **Total Questions:** {mc_total}
                    - **Answered:** {mc_answered} ({mc_answered/mc_total*100:.1f}%)
                    - **Correct:** {mc_correct} ({mc_percentage:.1f}%)
                    - **Incorrect:** {mc_incorrect} ({mc_incorrect/mc_total*100:.1f}%)
                    - **Unanswered:** {mc_unanswered} ({mc_unanswered/mc_total*100:.1f}%)
                    """)
                    
                    # Performance indicator
                    if mc_percentage >= 90:
                        st.success("🌟 Excellent performance!")
                    elif mc_percentage >= 70:
                        st.info("👍 Good performance!")
                    elif mc_percentage >= 50:
                        st.warning("📚 Keep practicing!")
                    else:
                        st.error("📖 Review the material and try again!")
                else:
                    st.write("No multiple choice questions in this quiz.")
            
            with breakdown_col2:
                st.markdown("**Short Answer Questions Analysis**")
                if sa_total > 0:
                    sa_completion = (sa_answered / sa_total * 100) if sa_total > 0 else 0
                    st.progress(sa_completion / 100, text=f"Completion: {sa_completion:.1f}%")
                    
                    st.markdown(f"""
                    - **Total Questions:** {sa_total}
                    - **Answered:** {sa_answered} ({sa_completion:.1f}%)
                    - **Unanswered:** {sa_unanswered} ({sa_unanswered/sa_total*100:.1f}%)
                    """)
                    # Calculate short answer correct count
                    sa_correct = sum(1 for i, q in enumerate(questions, 1) 
                                   if q.get('question_type') == 'short_answer' 
                                   and st.session_state.quiz_answers.get(f"q_{i}", "").strip()
                                   and st.session_state.get(f"eval_q_{i}", {}).get("is_correct", False))
                    if sa_correct > 0:
                        st.write(f"- **Correct:** {sa_correct} ({sa_correct/sa_total*100:.1f}%)")
                    st.info("💡 Short answer questions are automatically evaluated using AI.")
                else:
                    st.write("No short answer questions in this quiz.")
            
            # Question-by-Question Performance
            st.markdown("---")
            st.markdown("#### 📋 Question-by-Question Performance")
            
            # Create a performance table
            performance_data = []
            for i, question in enumerate(questions, 1):
                question_key = f"q_{i}"
                question_type = question.get("question_type", "")
                correct_answer = question.get("correct_answer", "")
                
                status = "❌ Unanswered"
                is_correct = False
                
                if question_type == "multiple_choice":
                    user_answer_idx = st.session_state.quiz_answers.get(question_key)
                    if user_answer_idx is not None:
                        options = question.get("options", [])
                        option_labels = []
                        for opt in options:
                            if ") " in opt:
                                option_labels.append(opt.split(")")[0] + ")")
                            else:
                                idx = options.index(opt)
                                option_labels.append(chr(65 + idx) + ")")
                        
                        if user_answer_idx < len(option_labels):
                            user_selected = option_labels[user_answer_idx]
                            is_correct = user_selected == correct_answer or correct_answer.startswith(user_selected.replace(")", ""))
                            status = "✅ Correct" if is_correct else "❌ Incorrect"
                elif question_type == "short_answer":
                    user_answer = st.session_state.quiz_answers.get(question_key, "").strip()
                    if user_answer:
                        eval_key = f"eval_{question_key}"
                        evaluation = st.session_state.get(eval_key, {})
                        is_correct = evaluation.get("is_correct", False)
                        status = "✅ Correct" if is_correct else "❌ Incorrect"
                    else:
                        status = "❌ Unanswered"
                
                performance_data.append({
                    "Question": i,
                    "Type": "MC" if question_type == "multiple_choice" else "SA",
                    "Status": status,
                    "Correct": "Yes" if is_correct else ("N/A" if question_type == "short_answer" else "No")
                })
            
            # Display performance table
            df = pd.DataFrame(performance_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Performance Insights
            st.markdown("---")
            st.markdown("#### 💡 Performance Insights & Recommendations")
            
            insights = []
            if completion_rate < 50:
                insights.append("⚠️ **Low Completion Rate:** You answered less than half of the questions. Try to attempt all questions for better learning.")
            elif completion_rate < 80:
                insights.append("📝 **Moderate Completion:** Good effort! Try to answer all questions next time.")
            else:
                insights.append("✅ **Excellent Completion:** You answered most/all questions. Great commitment!")
            
            if mc_total > 0:
                if mc_percentage >= 90:
                    insights.append("🌟 **Outstanding Accuracy:** You have a strong understanding of the material!")
                elif mc_percentage >= 70:
                    insights.append("👍 **Good Accuracy:** You're on the right track. Keep reviewing the incorrect answers.")
                elif mc_percentage >= 50:
                    insights.append("📚 **Average Performance:** Review the material and focus on the topics you got wrong.")
                else:
                    insights.append("📖 **Needs Improvement:** Take time to review the material and understand the concepts better.")
            
            if mc_incorrect > 0:
                insights.append(f"🎯 **Focus Areas:** Review {mc_incorrect} incorrect answer(s) to improve your understanding.")
            
            if sa_total > 0 and sa_unanswered > 0:
                insights.append(f"📝 **Short Answers:** You have {sa_unanswered} unanswered short answer question(s). Review them for comprehensive learning.")
            
            for insight in insights:
                st.markdown(insight)
            
            st.markdown("---")
            st.info("💡 **Note:** Short answer questions are not auto-scored. Please review them manually by comparing your answers with the correct answers shown below.")
            
            if st.button("Reset Quiz"):
                st.session_state.quiz_answers = {}
                st.session_state.show_results = False
                st.rerun()

        # Download button
        import json

        quiz_json = json.dumps(quiz_data, indent=2)
        st.download_button(
            label="📥 Download Quiz (JSON)",
            data=quiz_json,
            file_name="quiz.json",
            mime="application/json",
        )

# Sidebar
with st.sidebar:
    st.info(f"📄 Document ID: `{st.session_state.document_id}`")

    if st.button("Clear Quiz"):
        st.session_state.generated_quiz = None
        st.rerun()

