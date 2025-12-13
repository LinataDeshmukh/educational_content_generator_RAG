"""Quiz generation router."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from fastapi_backend.dependencies import get_content_generator
from fastapi_backend.models.schemas import (
    ErrorResponse,
    EvaluateAnswerRequest,
    EvaluateAnswerResponse,
    QuizRequest,
    QuizResponse,
)
from fastapi_backend.services.content_generator import ContentGenerator
from fastapi_backend.utils.errors import ContentGenerationError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/quiz", tags=["quiz"])


@router.post(
    "/",
    response_model=QuizResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def generate_quiz(
    request: QuizRequest,
    content_generator: ContentGenerator = Depends(get_content_generator),
) -> QuizResponse:
    """
    Generate a quiz from the indexed content.

    Args:
        request: Quiz generation request
        content_generator: Content generation service

    Returns:
        QuizResponse with generated quiz

    Raises:
        HTTPException: If generation fails
    """
    try:
        try:
            quiz_data = content_generator.generate_quiz(
                num_questions=request.num_questions,
                question_types=request.question_types,
                namespace=request.document_id,
            )
        except ContentGenerationError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Quiz generation failed: {str(e)}",
            )

        return QuizResponse(quiz=quiz_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during quiz generation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.post(
    "/evaluate-answer",
    response_model=EvaluateAnswerResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def evaluate_answer(
    request: EvaluateAnswerRequest,
    content_generator: ContentGenerator = Depends(get_content_generator),
) -> EvaluateAnswerResponse:
    """
    Evaluate a short answer question using LLM.

    Args:
        request: Evaluation request with user answer, correct answer, and question
        content_generator: Content generation service

    Returns:
        EvaluateAnswerResponse with is_correct and feedback

    Raises:
        HTTPException: If evaluation fails
    """
    try:
        try:
            evaluation = content_generator.evaluate_answer(
                user_answer=request.user_answer,
                correct_answer=request.correct_answer,
                question=request.question,
            )
        except ContentGenerationError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Answer evaluation failed: {str(e)}",
            )

        return EvaluateAnswerResponse(
            is_correct=evaluation.get("is_correct", False),
            feedback=evaluation.get("feedback", ""),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during answer evaluation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )

