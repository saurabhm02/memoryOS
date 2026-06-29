"""Answer-scoring adapters for the AnswerScorer port.

``GeminiAnswerScorer`` is the production grader (LiteLLM → the configured Gemini model).
``FakeAnswerScorer`` is the deterministic test double.
"""

from .fake import FakeAnswerScorer
from .gemini_scorer import GeminiAnswerScorer

__all__ = ["FakeAnswerScorer", "GeminiAnswerScorer"]
