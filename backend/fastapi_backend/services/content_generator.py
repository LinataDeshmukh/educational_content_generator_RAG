"""Content generation service for quizzes, summaries, and flashcards."""

import json
import logging
from typing import Any, Optional

from llama_index.core.llms import LLM
from llama_index.llms.openai import OpenAI

from fastapi_backend.config import settings
from fastapi_backend.services.rag_service import RAGService
from fastapi_backend.utils.errors import ContentGenerationError

logger = logging.getLogger(__name__)


class ContentGenerator:
    """Service for generating educational content from indexed documents."""

    def __init__(self, rag_service: RAGService, llm: Optional[LLM] = None):
        """
        Initialize the content generator.

        Args:
            rag_service: RAG service instance for retrieving context
            llm: Optional LLM (defaults to OpenAI)
        """
        self.rag_service = rag_service

        if llm:
            self.llm = llm
        else:
            self.llm = OpenAI(
                model=settings.llm_model,
                temperature=settings.llm_temperature,
                api_key=settings.openai_api_key,
            )

    def generate_quiz(
        self,
        num_questions: int = 10,
        question_types: Optional[list[str]] = None,
        namespace: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Generate a quiz from the indexed content.

        Args:
            num_questions: Number of questions to generate
            question_types: List of question types (e.g., ["multiple_choice", "short_answer"])
            namespace: Optional namespace to query

        Returns:
            Dictionary with quiz questions and answers

        Raises:
            ContentGenerationError: If generation fails
        """
        if question_types is None:
            question_types = ["multiple_choice", "short_answer"]

        try:
            # Retrieve diverse context from the document
            context_chunks = self.rag_service.retrieve_context(
                query="key concepts important topics main ideas",
                top_k=10,
                namespace=namespace,
            )

            # Combine context
            context_text = "\n\n".join(
                [chunk["text"] for chunk in context_chunks]
            )

            # Create prompt for quiz generation
            question_types_str = ", ".join(question_types)
            prompt = f"""Generate a comprehensive quiz based on the following educational content.

Content:
{context_text}

Requirements:
- Generate exactly {num_questions} questions
- Include a mix of question types: {question_types_str}
- For multiple choice questions, provide 4 options (A, B, C, D) with exactly one correct answer
- For short answer questions, provide a clear, concise answer
- Questions should cover different topics from the content
- Questions should test understanding, not just recall

CRITICAL: Each question MUST include sufficient context so the question is self-contained and understandable without referring back to the document. For example:
- BAD: "What did the initial test assertion fail?" (too vague - what test? what assertion?)
- GOOD: "In the Selenium setup example, the initial test assertion failed because the expected heading did not match. What was the specific reason for this failure?" (includes context)

For each question:
1. Include relevant context from the content that makes the question clear
2. Reference specific examples, scenarios, or concepts mentioned in the content
3. Make sure someone reading just the question understands what is being asked
4. For multiple choice, ensure the question and options together provide enough context

IMPORTANT - Hint Generation:
- The hint MUST be specific to the correct answer and guide the user toward it
- For multiple choice: The hint should point to characteristics, features, or context that relates to the correct option
- For short answer: The hint should suggest key concepts, terms, or context related to the correct answer
- The hint should NOT directly state the answer, but should make it easier to identify
- Examples:
  * If correct answer is about "Selenium WebDriver", hint: "Think about the tool used for browser automation in the setup example"
  * If correct answer is about "Maven dependencies", hint: "Consider what needs to be added to the pom.xml file"
  * If correct answer is about "assertion failure", hint: "What happens when expected and actual values don't match?"

- Format the response as a JSON object with the following structure:
{{
  "quiz_title": "Title of the quiz",
  "questions": [
    {{
      "question_number": 1,
      "question_type": "multiple_choice" or "short_answer",
      "question": "Contextual question text that includes relevant background information",
      "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"] (only for multiple_choice),
      "correct_answer": "Correct answer or option letter",
      "hint": "A specific hint that guides toward the correct answer by referencing key concepts, context, or characteristics related to the answer",
      "explanation": "Brief explanation of the answer with reference to the content"
    }}
  ]
}}

Return only valid JSON, no additional text."""

            # Generate quiz using LLM
            response = self.llm.complete(prompt)
            quiz_text = str(response).strip()

            # Parse JSON response
            # Remove markdown code blocks if present
            if quiz_text.startswith("```"):
                quiz_text = quiz_text.split("```")[1]
                if quiz_text.startswith("json"):
                    quiz_text = quiz_text[4:]
                quiz_text = quiz_text.strip()

            quiz_data = json.loads(quiz_text)

            logger.info(
                f"Generated quiz with {len(quiz_data.get('questions', []))} questions"
            )

            return quiz_data

        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse quiz JSON: {str(e)}"
            logger.error(error_msg)
            raise ContentGenerationError(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to generate quiz: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise ContentGenerationError(error_msg) from e

    def generate_competitive_quiz_bank(
        self,
        num_questions: int = 50,
        topic: Optional[str] = None,
        namespace: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Generate a question bank for competitive quiz with difficulty levels.

        Args:
            num_questions: Number of questions to generate (default 50)
            topic: Optional specific topic to focus on
            namespace: Optional namespace to query

        Returns:
            List of questions with difficulty levels assigned

        Raises:
            ContentGenerationError: If generation fails
        """
        try:
            # Build query based on topic or general
            if topic:
                query = f"{topic} key concepts important topics"
            else:
                query = "key concepts important topics main ideas diverse content"

            # Retrieve diverse context (CRITICAL: use namespace for document isolation)
            logger.info(
                f"Generating competitive quiz bank: num_questions={num_questions}, "
                f"topic={topic}, namespace={namespace}"
            )
            context_chunks = self.rag_service.retrieve_context(
                query=query,
                top_k=20,  # Get more context for diverse questions
                namespace=namespace,  # IMPORTANT: Filter by namespace to only use current document
            )
            
            if not context_chunks:
                logger.warning(
                    f"No context retrieved for namespace '{namespace}'. "
                    "This might mean the document was not indexed correctly or namespace is wrong."
                )
            else:
                logger.info(
                    f"Retrieved {len(context_chunks)} context chunks from namespace '{namespace}'"
                )

            # Combine context
            context_text = "\n\n".join([chunk["text"] for chunk in context_chunks])

            # Calculate distribution: ~30% low, ~40% medium, ~30% hard
            low_count = int(num_questions * 0.3)
            medium_count = int(num_questions * 0.4)
            hard_count = num_questions - low_count - medium_count

            prompt = f"""Generate a comprehensive question bank for a competitive adaptive quiz based on the following educational content.

Content:
{context_text}

Requirements:
- Generate exactly {num_questions} multiple choice questions (MCQ)
- Each question must have exactly 4 options (A, B, C, D) with exactly one correct answer
- Questions should cover diverse topics from the content
- Questions should test understanding, not just recall
- Each question MUST be self-contained with sufficient context

Difficulty Distribution:
- {low_count} questions should be LOW difficulty (basic concepts, definitions, straightforward facts)
- {medium_count} questions should be MEDIUM difficulty (application of concepts, moderate complexity)
- {hard_count} questions should be HARD difficulty (complex analysis, synthesis, advanced concepts)

For each question, assign a difficulty level based on:
- LOW: Basic recall, simple definitions, straightforward facts
- MEDIUM: Application of concepts, moderate problem-solving, connecting ideas
- HARD: Complex analysis, synthesis of multiple concepts, advanced reasoning

IMPORTANT - Hint Generation:
- Each question MUST include a hint field
- The hint should guide the user toward the correct answer without directly revealing it
- The hint should reference key concepts, context, or characteristics related to the correct answer
- For example: "Think about the tool used for browser automation" or "Consider what needs to be added to configuration files"

Format the response as a JSON object with the following structure:
{{
  "questions": [
    {{
      "question_id": "q1",
      "difficulty": "low" or "medium" or "hard",
      "question": "Contextual question text with sufficient background information",
      "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
      "correct_answer": "A" (or B, C, D),
      "hint": "A specific hint that guides toward the correct answer by referencing key concepts or context",
      "explanation": "Brief explanation of why this answer is correct"
    }}
  ]
}}

Return only valid JSON, no additional text."""

            # Generate question bank using LLM
            response = self.llm.complete(prompt)
            quiz_text = str(response).strip()

            # Parse JSON response
            if quiz_text.startswith("```"):
                quiz_text = quiz_text.split("```")[1]
                if quiz_text.startswith("json"):
                    quiz_text = quiz_text[4:]
                quiz_text = quiz_text.strip()

            quiz_data = json.loads(quiz_text)
            questions = quiz_data.get("questions", [])

            # Validate and add question_id if missing
            for idx, question in enumerate(questions):
                if "question_id" not in question:
                    question["question_id"] = f"q{idx + 1}"

            logger.info(
                f"Generated competitive quiz bank with {len(questions)} questions "
                f"(Low: {sum(1 for q in questions if q.get('difficulty') == 'low')}, "
                f"Medium: {sum(1 for q in questions if q.get('difficulty') == 'medium')}, "
                f"Hard: {sum(1 for q in questions if q.get('difficulty') == 'hard')})"
            )

            return questions

        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse question bank JSON: {str(e)}"
            logger.error(error_msg)
            raise ContentGenerationError(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to generate competitive quiz bank: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise ContentGenerationError(error_msg) from e

    def generate_summary(
        self,
        length: str = "medium",
        namespace: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Generate a summary of the indexed content.

        Args:
            length: Summary length ("short", "medium", "long")
            namespace: Optional namespace to query

        Returns:
            Dictionary with summary text and metadata

        Raises:
            ContentGenerationError: If generation fails
        """
        try:
            # Retrieve comprehensive context
            context_chunks = self.rag_service.retrieve_context(
                query="main topics key points summary overview",
                top_k=15,
                namespace=namespace,
            )

            # Combine context
            context_text = "\n\n".join(
                [chunk["text"] for chunk in context_chunks]
            )

            # Determine target length
            length_guidance = {
                "short": "2-3 paragraphs (approximately 150-200 words)",
                "medium": "4-6 paragraphs (approximately 300-400 words)",
                "long": "8-10 paragraphs (approximately 600-800 words)",
            }
            target_length = length_guidance.get(length, length_guidance["medium"])

            # Create prompt for summary generation
            prompt = f"""Generate a comprehensive summary of the following educational content.

Content:
{context_text}

Requirements:
- Create a well-structured summary that captures the main ideas and key concepts
- Target length: {target_length}
- Organize the summary with clear sections if appropriate
- Include important details while maintaining conciseness
- Use clear, academic language
- Format the response as a JSON object with the following structure:
{{
  "summary_title": "Title of the summary",
  "summary": "The summary text here",
  "key_topics": ["topic1", "topic2", "topic3"],
  "word_count": approximate word count
}}

Return only valid JSON, no additional text."""

            # Generate summary using LLM
            response = self.llm.complete(prompt)
            summary_text = str(response).strip()

            # Parse JSON response
            if summary_text.startswith("```"):
                summary_text = summary_text.split("```")[1]
                if summary_text.startswith("json"):
                    summary_text = summary_text[4:]
                summary_text = summary_text.strip()

            summary_data = json.loads(summary_text)

            logger.info(f"Generated {length} summary")

            return summary_data

        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse summary JSON: {str(e)}"
            logger.error(error_msg)
            raise ContentGenerationError(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to generate summary: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise ContentGenerationError(error_msg) from e

    def generate_flashcards(
        self,
        num_flashcards: int = 20,
        namespace: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Generate flashcards from the indexed content.

        Args:
            num_flashcards: Number of flashcards to generate
            namespace: Optional namespace to query

        Returns:
            Dictionary with flashcards (front/back pairs)

        Raises:
            ContentGenerationError: If generation fails
        """
        try:
            # Retrieve diverse context
            context_chunks = self.rag_service.retrieve_context(
                query="definitions concepts terms key vocabulary important facts",
                top_k=12,
                namespace=namespace,
            )

            # Combine context
            context_text = "\n\n".join(
                [chunk["text"] for chunk in context_chunks]
            )

            # Create prompt for flashcard generation
            prompt = f"""Generate educational flashcards based on the following content.

Content:
{context_text}

Requirements:
- Generate exactly {num_flashcards} flashcards
- Each flashcard should have a clear front (question/term) and back (answer/definition)
- Cover important concepts, definitions, facts, and key information
- Front side should be concise (1-2 sentences or a term)
- Back side should provide a clear, informative answer (2-4 sentences)
- Format the response as a JSON object with the following structure:
{{
  "flashcard_set_title": "Title of the flashcard set",
  "flashcards": [
    {{
      "card_number": 1,
      "front": "Question or term",
      "back": "Answer or definition",
      "category": "Optional category (e.g., 'definition', 'concept', 'fact')"
    }}
  ]
}}

Return only valid JSON, no additional text."""

            # Generate flashcards using LLM
            response = self.llm.complete(prompt)
            flashcards_text = str(response).strip()

            # Parse JSON response
            if flashcards_text.startswith("```"):
                flashcards_text = flashcards_text.split("```")[1]
                if flashcards_text.startswith("json"):
                    flashcards_text = flashcards_text[4:]
                flashcards_text = flashcards_text.strip()

            flashcards_data = json.loads(flashcards_text)

            logger.info(
                f"Generated {len(flashcards_data.get('flashcards', []))} flashcards"
            )

            return flashcards_data

        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse flashcards JSON: {str(e)}"
            logger.error(error_msg)
            raise ContentGenerationError(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to generate flashcards: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise ContentGenerationError(error_msg) from e

    def evaluate_answer(
        self, user_answer: str, correct_answer: str, question: str
    ) -> dict[str, Any]:
        """
        Evaluate a short answer using LLM to determine if it's correct.

        Args:
            user_answer: User's answer to evaluate
            correct_answer: Correct answer
            question: The question that was asked

        Returns:
            Dictionary with is_correct boolean and feedback

        Raises:
            ContentGenerationError: If evaluation fails
        """
        try:
            prompt = f"""Evaluate if the user's answer is correct for the following question.

Question: {question}

Correct Answer: {correct_answer}

User's Answer: {user_answer}

Instructions:
- Compare the user's answer with the correct answer
- Consider semantic similarity, key concepts, and meaning (not just exact word matching)
- The answer can be correct even if worded differently, as long as it conveys the same meaning
- Be lenient with minor spelling/grammar differences, but ensure the core concept is correct
- Return ONLY a JSON object with this exact structure:
{{
  "is_correct": true or false,
  "feedback": "Brief explanation of why the answer is correct or incorrect"
}}

Return only valid JSON, no additional text."""

            # Generate evaluation using LLM
            response = self.llm.complete(prompt)
            evaluation_text = str(response).strip()

            # Parse JSON response
            if evaluation_text.startswith("```"):
                evaluation_text = evaluation_text.split("```")[1]
                if evaluation_text.startswith("json"):
                    evaluation_text = evaluation_text[4:]
                evaluation_text = evaluation_text.strip()

            evaluation_data = json.loads(evaluation_text)

            logger.info(
                f"Evaluated answer: is_correct={evaluation_data.get('is_correct', False)}"
            )

            return evaluation_data

        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse evaluation JSON: {str(e)}"
            logger.error(error_msg)
            # Fallback: do simple comparison
            user_lower = user_answer.lower().strip()
            correct_lower = correct_answer.lower().strip()
            is_similar = user_lower in correct_lower or correct_lower in user_lower
            return {
                "is_correct": is_similar,
                "feedback": "Answer evaluated using simple comparison due to parsing error.",
            }
        except Exception as e:
            error_msg = f"Failed to evaluate answer: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise ContentGenerationError(error_msg) from e

