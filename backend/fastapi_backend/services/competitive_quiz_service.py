"""Service for managing competitive quiz sessions with adaptive learning."""

import logging
import random
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from fastapi_backend.services.content_generator import ContentGenerator
from fastapi_backend.utils.adaptive_learning import (
    AdaptiveQuizManager,
    DifficultyLevel,
)
from fastapi_backend.utils.errors import ContentGenerationError

logger = logging.getLogger(__name__)


class CompetitiveQuizService:
    """Service for managing competitive quiz with adaptive difficulty."""

    def __init__(self, content_generator: ContentGenerator):
        """
        Initialize competitive quiz service.

        Args:
            content_generator: Content generator for question bank generation
        """
        self.content_generator = content_generator
        self.adaptive_manager = AdaptiveQuizManager()

        # In-memory storage for quiz sessions
        # In production, use Redis or database
        self.question_banks: Dict[str, List[Dict[str, Any]]] = {}
        self.quiz_sessions: Dict[str, Dict[str, Any]] = {}

    def generate_question_bank(
        self,
        num_questions: int = 50,
        topic: Optional[str] = None,
        document_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate question bank for competitive quiz.

        Args:
            num_questions: Number of questions in bank (default 50)
            topic: Optional specific topic
            document_id: Optional document ID

        Returns:
            Dictionary with question_bank and quiz_id
        """
        try:
            # Generate question bank
            question_bank = self.content_generator.generate_competitive_quiz_bank(
                num_questions=num_questions,
                topic=topic,
                namespace=document_id,
            )

            # Generate unique quiz ID
            quiz_id = str(uuid.uuid4())

            # Store question bank
            self.question_banks[quiz_id] = question_bank

            logger.info(
                f"Generated question bank with {len(question_bank)} questions "
                f"(quiz_id: {quiz_id})"
            )

            return {
                "question_bank": question_bank,
                "quiz_id": quiz_id,
            }

        except ContentGenerationError as e:
            raise
        except Exception as e:
            error_msg = f"Failed to generate question bank: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise ContentGenerationError(error_msg) from e

    def start_quiz(
        self, quiz_id: str, num_questions: int = 10
    ) -> Dict[str, Any]:
        """
        Start a competitive quiz session.

        Args:
            quiz_id: Quiz ID from question bank
            num_questions: Number of questions in quiz (5-10)

        Returns:
            Dictionary with first question and session info
        """
        if quiz_id not in self.question_banks:
            raise ContentGenerationError(f"Quiz ID {quiz_id} not found")

        question_bank = self.question_banks[quiz_id]

        # Create session
        session_id = str(uuid.uuid4())
        current_difficulty = DifficultyLevel.MEDIUM.value  # Start with medium

        # Initialize session state
        session = {
            "session_id": session_id,
            "quiz_id": quiz_id,
            "question_bank": question_bank,
            "num_questions": num_questions,
            "current_question_index": 0,
            "questions_answered": 0,
            "correct_answers": 0,
            "answers": [],  # List of (question_id, answer, is_correct, difficulty)
            "performance_history": [],  # List of recent answers (bool)
            "current_difficulty": current_difficulty,
            "total_reward": 0.0,
            "started_at": datetime.now().isoformat(),
        }

        self.quiz_sessions[session_id] = session

        # Get first question based on initial difficulty
        first_question = self._get_next_question(session, current_difficulty)

        logger.info(
            f"Started competitive quiz session {session_id} "
            f"(quiz_id: {quiz_id}, num_questions: {num_questions})"
        )

        return {
            "question": first_question,
            "session_id": session_id,
            "current_difficulty": current_difficulty,
        }

    def submit_answer(
        self, session_id: str, question_id: str, answer: str
    ) -> Dict[str, Any]:
        """
        Submit an answer and get next question.

        Args:
            session_id: Session ID
            question_id: Question ID
            answer: User's answer

        Returns:
            Dictionary with answer result and next question
        """
        if session_id not in self.quiz_sessions:
            raise ContentGenerationError(f"Session ID {session_id} not found")

        session = self.quiz_sessions[session_id]

        # Find question in bank
        question = None
        for q in session["question_bank"]:
            if q.get("question_id") == question_id:
                question = q
                break

        if not question:
            raise ContentGenerationError(f"Question ID {question_id} not found")

        # Check if answer is correct
        correct_answer = question.get("correct_answer", "").strip().upper()
        user_answer = answer.strip().upper()

        # Handle both letter answers (A, B, C, D) and full option text
        is_correct = False
        if user_answer == correct_answer:
            is_correct = True
        else:
            # Check if user answer matches option text
            options = question.get("options", [])
            for opt in options:
                if opt.startswith(user_answer) or user_answer in opt.upper():
                    if opt.startswith(correct_answer):
                        is_correct = True
                    break

        # Get current difficulty
        current_difficulty = session["current_difficulty"]

        # Calculate reward
        reward = self.adaptive_manager.calculate_reward(
            is_correct, current_difficulty
        )

        # Update session
        session["answers"].append(
            {
                "question_id": question_id,
                "answer": answer,
                "is_correct": is_correct,
                "difficulty": current_difficulty,
                "reward": reward,
            }
        )
        session["performance_history"].append(is_correct)
        session["questions_answered"] += 1
        session["total_reward"] += reward

        if is_correct:
            session["correct_answers"] += 1

        # Calculate performance trend
        performance_trend = self.adaptive_manager.calculate_performance_trend(
            session["performance_history"]
        )

        # Update learning algorithms
        self.adaptive_manager.update_learning(
            current_difficulty=current_difficulty,
            next_difficulty=current_difficulty,  # Will be updated below
            performance_trend=performance_trend,
            reward=reward,
            use_thompson_sampling=True,
        )

        # Check if quiz is complete
        is_complete = session["questions_answered"] >= session["num_questions"]

        next_question = None
        next_difficulty = None

        if not is_complete:
            # Select next difficulty using adaptive algorithm
            # Key: Increase difficulty on correct, decrease on wrong
            next_difficulty = self.adaptive_manager.select_next_difficulty(
                current_difficulty=current_difficulty,
                performance_trend=performance_trend,
                last_answer_correct=is_correct,  # Pass correctness to guide difficulty
                use_thompson_sampling=True,
            )

            # Update session difficulty
            session["current_difficulty"] = next_difficulty

            # Get next question
            next_question = self._get_next_question(session, next_difficulty)

            session["current_question_index"] += 1

        # Calculate stats
        stats = self._calculate_stats(session)

        logger.info(
            f"Answer submitted: session={session_id}, question={question_id}, "
            f"correct={is_correct}, reward={reward:.2f}, "
            f"next_difficulty={next_difficulty}"
        )

        return {
            "is_correct": is_correct,
            "correct_answer": correct_answer,
            "explanation": question.get("explanation", ""),
            "reward": reward,
            "next_question": next_question,
            "next_difficulty": next_difficulty,
            "is_complete": is_complete,
            "stats": stats,
        }

    def _get_next_question(
        self, session: Dict[str, Any], difficulty: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get next question of specified difficulty.

        Args:
            session: Session dictionary
            difficulty: Desired difficulty level

        Returns:
            Question dictionary or None if no more questions
        """
        question_bank = session["question_bank"]
        answered_question_ids = {
            ans["question_id"] for ans in session["answers"]
        }

        # Filter questions by difficulty and not yet answered
        available_questions = [
            q
            for q in question_bank
            if q.get("difficulty", "").lower() == difficulty.lower()
            and q.get("question_id") not in answered_question_ids
        ]

        if not available_questions:
            # Fallback: get any unanswered question
            available_questions = [
                q
                for q in question_bank
                if q.get("question_id") not in answered_question_ids
            ]

        if not available_questions:
            return None

        # Select random question from available
        return random.choice(available_questions)

    def _calculate_stats(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate quiz statistics."""
        total = session["questions_answered"]
        correct = session["correct_answers"]
        accuracy = (correct / total * 100) if total > 0 else 0.0

        # Difficulty distribution
        difficulty_counts = {}
        for ans in session["answers"]:
            diff = ans["difficulty"]
            difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1

        return {
            "total_questions": session["num_questions"],
            "questions_answered": total,
            "correct_answers": correct,
            "accuracy": round(accuracy, 2),
            "total_reward": round(session["total_reward"], 2),
            "difficulty_distribution": difficulty_counts,
            "performance_trend": self.adaptive_manager.calculate_performance_trend(
                session["performance_history"]
            ),
        }

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID."""
        return self.quiz_sessions.get(session_id)

