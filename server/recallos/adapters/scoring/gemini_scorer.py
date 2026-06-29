"""GeminiAnswerScorer — grades answers via LiteLLM against the configured Gemini model.

A direct LLM call (not routed through Cognee — Cognee is the memory engine, not a
general grader). Provider-agnostic by config: point ``llm_model`` elsewhere and this same
adapter follows. Output is strict JSON, defensively parsed and clamped; any failure
raises ``ScoringError`` so a bad grade is never invented.
"""

from __future__ import annotations

import json
from collections.abc import Awaitable, Callable

from recallos.config import settings
from recallos.core.domain.errors import ScoringError
from recallos.core.domain.scoring import AnswerAssessment

_SYSTEM = (
    "You are a strict but fair senior software-engineering interviewer. You grade a "
    "candidate's answer about ONE backend concept on a 0-5 rubric: "
    "0 = no understanding, 2 = partial/with misconceptions, 3 = adequate, "
    "4 = solid, 5 = expert and complete. Reply ONLY with JSON of the form "
    '{"score": <int 0-5>, "rationale": "<one or two sentences>", '
    '"demonstrated": ["<sub-concepts the answer got right>"], '
    '"missed": ["<key sub-concepts the answer omitted or got wrong>"]}. '
    "Be concise and specific; do not invent facts the candidate did not state."
)


def _user_prompt(concept: str, question: str, answer: str) -> str:
    return (
        f"Concept: {concept}\n"
        f"Question: {question or '(no question text provided)'}\n"
        f"Candidate answer:\n{answer}\n\n"
        "Grade it as instructed."
    )


Completion = Callable[[list[dict[str, str]]], Awaitable[str]]


class GeminiAnswerScorer:
    def __init__(
        self,
        *,
        model: str | None = None,
        api_key: str | None = None,
        completion: Completion | None = None,
    ) -> None:
        self._model = model or settings.llm_model
        self._api_key = api_key or settings.resolved_gemini_key()
        # `completion` is injectable so tests grade without a network call.
        self._completion = completion

    async def score(
        self, *, concept: str, question: str, answer: str
    ) -> AnswerAssessment:
        if not answer.strip():
            raise ScoringError("answer is empty")
        try:
            raw = await self._complete(concept, question, answer)
            data = json.loads(raw)
            score = max(0, min(5, int(round(float(data["score"])))))
            rationale = str(data.get("rationale", "")).strip()
            demonstrated = tuple(str(x) for x in data.get("demonstrated", []) if x)[:8]
            missed = tuple(str(x) for x in data.get("missed", []) if x)[:8]
        except ScoringError:
            raise
        except Exception as exc:  # noqa: BLE001 — any grading failure is a ScoringError
            raise ScoringError(f"could not grade the answer: {exc}") from exc

        return AnswerAssessment(
            score=score, rationale=rationale, demonstrated=demonstrated, missed=missed
        )

    async def _complete(self, concept: str, question: str, answer: str) -> str:
        messages = [
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": _user_prompt(concept, question, answer)},
        ]
        if self._completion is not None:
            return await self._completion(messages)

        import litellm

        response = await litellm.acompletion(
            model=self._model,
            api_key=self._api_key,
            messages=messages,
            temperature=0,
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content or ""
