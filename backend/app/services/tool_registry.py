from __future__ import annotations

from datetime import date, timedelta

from app.models.document import DocumentChunk
from app.services.agent_provider import CalculatorInput, DateOffsetInput, DocumentSearchInput, calculate
from app.services.retrieval_service import RetrievalService

MAX_TOOL_OUTPUT = 6000
MAX_TRACE_EVENTS = 40
MAX_AGENT_STEPS = 5
MAX_TOOLS_PER_REQUEST = 4


class ToolError(Exception):
    """A safe, user-displayable tool validation or execution failure."""


class ToolRegistry:
    def __init__(self, retrieval_service: RetrievalService) -> None:
        self._retrieval = retrieval_service
        self._handlers = {
            "document_search": (DocumentSearchInput, self._document_search),
            "calculator": (CalculatorInput, calculate),
            "date_offset": (DateOffsetInput, self._date_offset),
        }

    @property
    def names(self) -> set[str]:
        return set(self._handlers)

    def execute(self, name: str, arguments: dict) -> dict:
        if name not in self._handlers:
            raise ToolError("Requested tool is not available")
        schema, handler = self._handlers[name]
        try:
            payload = schema.model_validate(arguments)
            result = handler(payload)
            return self._bound_result(result)
        except ToolError:
            raise
        except Exception as exc:
            raise ToolError("Tool request was invalid or could not be completed") from exc

    def _document_search(self, payload: DocumentSearchInput) -> dict:
        chunks = self._retrieval.search(payload.query, payload.top_k)
        return {
            "tool": "document_search",
            "results": [
                {
                    "document_id": item.document_id,
                    "filename": item.filename,
                    "chunk_id": item.chunk_id,
                    "chunk_index": item.chunk_index,
                    "similarity": item.similarity,
                    "content": item.content[:1600],
                }
                for item in chunks
            ],
        }

    @staticmethod
    def _date_offset(payload: DateOffsetInput) -> dict:
        day = date.today() + timedelta(days=payload.days)
        return {"tool": "date_offset", "date": day.isoformat()}

    @staticmethod
    def _bound_result(value: dict) -> dict:
        text = str(value)
        if len(text) <= MAX_TOOL_OUTPUT:
            return value
        return {"tool": value.get("tool", "unknown"), "truncated": True, "preview": text[:MAX_TOOL_OUTPUT]}
