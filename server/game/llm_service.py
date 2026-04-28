"""LLM-based Question Generation Service.

Provides functionality to generate quiz questions using LLM models.
Supports both external (OpenAI) and local LLM models.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate_questions(
        self,
        num_questions: int,
        categories: Optional[List[str]] = None,
        context: Optional[List[str]] = None,
        difficulty_level: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Generate questions using LLM.

        Args:
            num_questions: Number of questions to generate
            categories: List of question categories (optional)
            context: List of related questions for context/RAG (optional)
            difficulty_level: Difficulty level (1-5, optional)

        Returns:
            Dictionary containing generated questions in JSON format
        """
        pass


class OpenAIQuestionGenerator(LLMProvider):
    """Question generator using OpenAI API."""

    def __init__(self, api_key: str, model: str = "gpt-4"):
        """Initialize OpenAI question generator.

        Args:
            api_key: OpenAI API key
            model: Model name (default: gpt-4)
        """
        self.api_key = api_key
        self.model = model

    def generate_questions(
        self,
        num_questions: int,
        categories: Optional[List[str]] = None,
        context: Optional[List[str]] = None,
        difficulty_level: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Generate questions using OpenAI API.

        Args:
            num_questions: Number of questions to generate
            categories: List of question categories
            context: Related questions for context
            difficulty_level: Difficulty level (1-5)

        Returns:
            Dictionary with generated questions
        """
        # TODO: Implement OpenAI API integration
        # This will use OpenAI's API to generate structured questions
        logger.info(
            f"Generating {num_questions} questions with OpenAI {self.model}"
        )
        pass


class QuestionGeneratorService:
    """Main service for LLM-based question generation."""

    def __init__(self, provider: LLMProvider):
        """Initialize the question generator service.

        Args:
            provider: LLM provider instance
        """
        self.provider = provider

    def generate_questions(
        self,
        num_questions: int = 5,
        categories: Optional[List[str]] = None,
        context: Optional[List[str]] = None,
        difficulty_level: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Generate questions with optional RAG context.

        Args:
            num_questions: Number of questions to generate (default: 5)
            categories: List of categories for questions (optional)
            context: List of existing questions for RAG (optional)
            difficulty_level: Difficulty level 1-5 (optional)

        Returns:
            Dictionary with:
            {
                "success": bool,
                "questions": [
                    {
                        "question": str,
                        "options": [str, str, str, str],
                        "correct_answer": int,
                        "category": str,
                        "difficulty": int
                    }
                ]
            }
        """
        try:
            result = self.provider.generate_questions(
                num_questions=num_questions,
                categories=categories,
                context=context,
                difficulty_level=difficulty_level,
            )
            return {"success": True, "questions": result}
        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}")
            return {"success": False, "error": str(e)}


def create_question_generator(
    provider_type: str = "openai", **kwargs
) -> QuestionGeneratorService:
    """Factory function to create question generator service.

    Args:
        provider_type: Type of provider ('openai' or 'local')
        **kwargs: Provider-specific arguments

    Returns:
        QuestionGeneratorService instance
    """
    if provider_type == "openai":
        provider = OpenAIQuestionGenerator(**kwargs)
    else:
        raise ValueError(f"Unknown provider type: {provider_type}")

    return QuestionGeneratorService(provider)
