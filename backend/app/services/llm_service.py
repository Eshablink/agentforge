from __future__ import annotations

from openai import OpenAI

from app.core.settings import get_settings
from app.services.provider_errors import ProviderConfig, ProviderError
from app.services.provider_utils import run_bounded


class LLMError(Exception):
    """Raised when LLM response generation fails (normalized, safe message)."""


class LLMService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.provider = self.settings.llm_provider.lower()
        self._client: OpenAI | None = None

        if self.provider == "openai":
            if not self.settings.openai_api_key:
                raise LLMError("OPENAI_API_KEY is required when llm provider is openai")
            self._client = OpenAI(
                api_key=self.settings.openai_api_key,
                timeout=self.settings.llm_timeout_seconds,
                max_retries=0,
            )

    def answer(self, question: str, context: str) -> str:
        if self.provider == "openai":
            assert self._client is not None
            return self._openai_answer(question=question, context=context)
        return self._fake_answer(question=question, context=context)

    def _openai_answer(self, *, question: str, context: str) -> str:
        def _call() -> str:
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
                    {"role": "user", "content": f"Question:\n{question}\n\nContext:\n{context}"},
                ],
            )
            return response.choices[0].message.content or ""

        try:
            return run_bounded(
                _call,
                timeout_seconds=self.settings.llm_timeout_seconds,
                max_retries=self.settings.llm_max_retries,
            )
        except ProviderConfig:
            raise
        except ProviderError as exc:
            raise LLMError(str(exc)) from exc

    def _fake_answer(self, question: str, context: str) -> str:
        if not context.strip():
            return "I could not find enough information in the uploaded documents to answer that."
        preview = context[:500]
        return (
            "Grounded answer (fake provider): Based on retrieved document context, "
            f"the question '{question}' is supported by: {preview}"
        )
