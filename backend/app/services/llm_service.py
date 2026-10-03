from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from openai import OpenAI

from app.core.settings import get_settings


class LLMError(Exception):
    """Raised when LLM response generation fails."""


class LLMService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.provider = self.settings.llm_provider.lower()
        self._client: OpenAI | None = None

        if self.provider == "openai":
            if not self.settings.openai_api_key:
                raise LLMError("OPENAI_API_KEY is required when llm provider is openai")
            self._client = OpenAI(api_key=self.settings.openai_api_key)

    def answer(self, question: str, context: str) -> str:
        if self.provider == "openai":
            assert self._client is not None
            response = self._client.chat.completions.create(
                model=self.settings.llm_model,
                temperature=0,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a grounded assistant. Use only the provided context. "
                            "If the context is insufficient, explicitly say so and do not fabricate."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Question:\n{question}\n\nContext:\n{context}",
                    },
                ],
            )
            return response.choices[0].message.content or ""

        return self._fake_answer(question=question, context=context)

    def _fake_answer(self, question: str, context: str) -> str:
        if not context.strip():
            return "I could not find enough information in the uploaded documents to answer that."

        preview = context[:500]
        return (
            "Grounded answer (fake provider): Based on retrieved document context, "
            f"the question '{question}' is supported by: {preview}"
        )
