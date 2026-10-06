"""Final-answer native delta adapters; tool decisions remain structured and validated.

The adapter sends only bounded question/context/allowlisted tool outputs. It never
returns provider frames, usage objects or reasoning. Callers own stream closure.
"""
from __future__ import annotations

import json
from collections.abc import Iterator

from app.services.agent_provider import DecisionRequest, LLMDecisionProvider, OpenAIDecisionProvider
from app.services.provider_utils import classify, run_bounded


class NativeStreamUnavailable(Exception):
    """Provider has no native delta API; safe to use completed-answer fallback."""


class NativeStreamFailure(Exception):
    """A native stream failed; never restart it after consuming output."""


def native_deltas(provider: LLMDecisionProvider, request: DecisionRequest) -> Iterator[str]:
    if not isinstance(provider, OpenAIDecisionProvider):
        raise NativeStreamUnavailable()
    messages = [
        {"role": "system", "content": "Answer using only the supplied tool evidence when needed. If evidence is missing, say so. Never include hidden reasoning."},
        {"role": "user", "content": (
            f"Question: {request.question[:5000]}\nConversation: {request.conversation_context[:8000]}\n"
            f"Validated tool outputs: {json.dumps(request.prior_tool_results[-3:], default=str)[:18000]}"
        )},
    ]
    try:
        stream = run_bounded(
            lambda: provider.client.chat.completions.create(
                model=provider.model, temperature=0, stream=True, messages=messages
            ),
            timeout_seconds=provider.settings.llm_timeout_seconds,
            max_retries=provider.settings.llm_max_retries,
        )
    except Exception as exc:
        raise NativeStreamFailure("AI provider unavailable") from exc
    try:
        for frame in stream:
            choices = getattr(frame, "choices", None)
            if not choices:
                continue
            delta = getattr(choices[0], "delta", None)
            content = getattr(delta, "content", None)
            if content is None:
                continue
            if not isinstance(content, str):
                raise NativeStreamFailure("Invalid AI provider delta")
            if content:
                yield content
    except Exception as exc:
        raise NativeStreamFailure("AI provider stream failed") from exc
    finally:
        close = getattr(stream, "close", None)
        if callable(close):
            close()
