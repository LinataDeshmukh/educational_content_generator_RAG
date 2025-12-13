"""API client for communicating with FastAPI backend."""

import os
from typing import Any, Optional

import httpx
from dotenv import load_dotenv

load_dotenv()

# Backend API URL
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")


class APIClient:
    """Client for making requests to the FastAPI backend."""

    def __init__(self, base_url: str = BACKEND_API_URL):
        """
        Initialize the API client.

        Args:
            base_url: Base URL of the FastAPI backend
        """
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(timeout=300.0)  # 5 minute timeout for large operations

    def upload_pdf(self, file_bytes: bytes, filename: str) -> dict[str, Any]:
        """
        Upload a single PDF file to the backend (legacy method for backward compatibility).

        Args:
            file_bytes: PDF file content as bytes
            filename: Name of the file

        Returns:
            Response dictionary with document_id and metadata

        Raises:
            httpx.HTTPError: If the request fails
        """
        return self.upload_pdf_multiple([(file_bytes, filename)])

    def upload_pdf_multiple(self, files_data: list[tuple[bytes, str]]) -> dict[str, Any]:
        """
        Upload one or more PDF files to the backend.

        Args:
            files_data: List of tuples (file_bytes, filename) for each PDF file

        Returns:
            Response dictionary with document_id and metadata

        Raises:
            httpx.HTTPError: If the request fails
        """
        # For multiple files with the same field name "files", httpx needs:
        # A list of tuples where each tuple is: (field_name, file_tuple)
        # file_tuple is: (filename, file_bytes, content_type) OR (filename, file_bytes)
        # When using List[UploadFile] in FastAPI, all files must have the same field name
        files = []
        for file_bytes, filename in files_data:
            # httpx format: (field_name, (filename, file_bytes, content_type))
            files.append(("files", (filename, file_bytes, "application/pdf")))
        
        try:
            response = self.client.post(f"{self.base_url}/upload/", files=files)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            # Extract detailed error message from response
            error_msg = str(e)
            if e.response is not None:
                try:
                    error_detail = e.response.json()
                    if "detail" in error_detail:
                        error_msg = error_detail["detail"]
                        # Re-raise with more informative message
                        raise httpx.HTTPStatusError(
                            message=f"Upload failed: {error_msg}",
                            request=e.request,
                            response=e.response
                        ) from e
                except (ValueError, KeyError):
                    # If JSON parsing fails, try to get text
                    try:
                        error_text = e.response.text
                        if error_text:
                            error_msg = error_text
                    except:
                        pass
            # Re-raise the original error if we couldn't extract details
            raise

    def chat(
        self, 
        question: str, 
        document_id: Optional[str] = None,
        filename: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Send a chat question to the backend.

        Args:
            question: User question
            document_id: Required document ID to scope the query (for session isolation)
            filename: Optional filename of the uploaded document(s)

        Returns:
            Response dictionary with answer and sources

        Raises:
            httpx.HTTPError: If the request fails
        """
        if not document_id:
            raise ValueError("document_id is required for session isolation")
        
        payload = {
            "question": question,
            "document_id": document_id
        }
        
        if filename:
            payload["filename"] = filename

        try:
            response = self.client.post(f"{self.base_url}/chat/", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            # Extract detailed error message from response
            error_msg = str(e)
            if e.response is not None:
                try:
                    error_detail = e.response.json()
                    if "detail" in error_detail:
                        error_msg = error_detail["detail"]
                except (ValueError, KeyError):
                    # If JSON parsing fails, try to get text
                    try:
                        error_text = e.response.text
                        if error_text:
                            error_msg = error_text
                    except:
                        pass
            raise httpx.HTTPStatusError(
                message=f"Chat failed: {error_msg}",
                request=e.request,
                response=e.response
            ) from e

    def generate_quiz(
        self,
        num_questions: int = 10,
        question_types: Optional[list[str]] = None,
        document_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Generate a quiz from the indexed content.

        Args:
            num_questions: Number of questions to generate
            question_types: Optional list of question types
            document_id: Optional document ID to scope the quiz

        Returns:
            Response dictionary with quiz data

        Raises:
            httpx.HTTPError: If the request fails
        """
        payload = {"num_questions": num_questions}
        if question_types:
            payload["question_types"] = question_types
        if document_id:
            payload["document_id"] = document_id

        response = self.client.post(f"{self.base_url}/quiz/", json=payload)
        response.raise_for_status()
        return response.json()

    def generate_summary(
        self, length: str = "medium", document_id: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Generate a summary of the indexed content.

        Args:
            length: Summary length ("short", "medium", "long")
            document_id: Optional document ID to scope the summary

        Returns:
            Response dictionary with summary data

        Raises:
            httpx.HTTPError: If the request fails
        """
        payload = {"length": length}
        if document_id:
            payload["document_id"] = document_id

        response = self.client.post(f"{self.base_url}/summary/", json=payload)
        response.raise_for_status()
        return response.json()

    def generate_flashcards(
        self, num_flashcards: int = 20, document_id: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Generate flashcards from the indexed content.

        Args:
            num_flashcards: Number of flashcards to generate
            document_id: Optional document ID to scope the flashcards

        Returns:
            Response dictionary with flashcards data

        Raises:
            httpx.HTTPError: If the request fails
        """
        payload = {"num_flashcards": num_flashcards}
        if document_id:
            payload["document_id"] = document_id

        response = self.client.post(f"{self.base_url}/flashcards/", json=payload)
        response.raise_for_status()
        return response.json()

    def evaluate_answer(
        self, user_answer: str, correct_answer: str, question: str
    ) -> dict[str, Any]:
        """
        Evaluate a short answer using LLM.

        Args:
            user_answer: User's answer to evaluate
            correct_answer: Correct answer
            question: The question that was asked

        Returns:
            Response dictionary with is_correct and feedback

        Raises:
            httpx.HTTPError: If the request fails
        """
        payload = {
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "question": question,
        }

        response = self.client.post(f"{self.base_url}/quiz/evaluate-answer", json=payload)
        response.raise_for_status()
        return response.json()

    def generate_competitive_quiz_bank(
        self,
        num_questions: int = 50,
        topic: Optional[str] = None,
        document_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Generate question bank for competitive quiz.

        Args:
            num_questions: Number of questions in bank (default 50)
            topic: Optional specific topic
            document_id: Optional document ID

        Returns:
            Response dictionary with question_bank and quiz_id

        Raises:
            httpx.HTTPError: If the request fails
        """
        payload = {"num_questions": num_questions}
        if topic:
            payload["topic"] = topic
        if document_id:
            payload["document_id"] = document_id

        response = self.client.post(
            f"{self.base_url}/competitive-quiz/generate-bank", json=payload
        )
        response.raise_for_status()
        return response.json()

    def start_competitive_quiz(
        self, quiz_id: str, num_questions: int = 10
    ) -> dict[str, Any]:
        """
        Start a competitive quiz session.

        Args:
            quiz_id: Quiz ID from question bank
            num_questions: Number of questions in quiz (5-10)

        Returns:
            Response dictionary with first question and session info

        Raises:
            httpx.HTTPError: If the request fails
        """
        payload = {"quiz_id": quiz_id, "num_questions": num_questions}

        response = self.client.post(
            f"{self.base_url}/competitive-quiz/start", json=payload
        )
        response.raise_for_status()
        return response.json()

    def submit_competitive_answer(
        self, session_id: str, question_id: str, answer: str
    ) -> dict[str, Any]:
        """
        Submit an answer in competitive quiz.

        Args:
            session_id: Session ID
            question_id: Question ID
            answer: User's answer

        Returns:
            Response dictionary with answer result and next question

        Raises:
            httpx.HTTPError: If the request fails
        """
        payload = {
            "session_id": session_id,
            "question_id": question_id,
            "answer": answer,
        }

        response = self.client.post(
            f"{self.base_url}/competitive-quiz/answer", json=payload
        )
        response.raise_for_status()
        return response.json()

    def list_documents(self) -> dict[str, Any]:
        """
        List all existing documents in Pinecone.

        Returns:
            Response dictionary with list of documents

        Raises:
            httpx.HTTPError: If the request fails
        """
        response = self.client.get(f"{self.base_url}/documents/list")
        response.raise_for_status()
        return response.json()

    def health_check(self) -> dict[str, Any]:
        """
        Check backend health.

        Returns:
            Health status dictionary

        Raises:
            httpx.HTTPError: If the request fails
        """
        response = self.client.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def close(self) -> None:
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Global client instance
api_client = APIClient()

