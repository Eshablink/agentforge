"""Deterministic, bounded reranking of owner-filtered pgvector candidates."""
from __future__ import annotations

import math
import re
from itertools import islice
from collections.abc import Iterable
from typing import TypeVar

T = TypeVar("T")
_WORDS = re.compile(r"[a-z0-9]+")


def _words(text: str) -> set[str]:
    return set(_WORDS.findall(text.lower()[:2000]))


def select_evidence(question: str, candidates: Iterable[T], *, limit: int, minimum_similarity: float = -1.0) -> list[T]:
    """Rank cosine candidates with a small lexical bonus; keep supplied provenance.

    The caller must enforce ownership in SQL *before* calling this function.
    Only 40 candidates are consumed, including for generator inputs.
    """
    if not 1 <= limit <= 10 or not math.isfinite(minimum_similarity) or not -1 <= minimum_similarity <= 1:
        raise ValueError("Invalid evidence limits")
    query = _words(question)
    ranked = []
    for item in islice(candidates, 40):
        similarity = float(item.similarity)
        if not math.isfinite(similarity) or similarity < minimum_similarity:
            continue
        terms = _words(item.content)
        overlap = len(query & terms) / len(query) if query else 0.0
        ranked.append((item, similarity + 0.1 * overlap))
    ranked.sort(key=lambda row: (-row[1], -float(row[0].similarity), str(row[0].document_id), row[0].chunk_index, str(row[0].chunk_id)))
    seen: set[str] = set()
    output = []
    for item, _ in ranked:
        key = " ".join(item.content.lower().split())[:800]
        if key in seen:
            continue
        seen.add(key)
        output.append(item)
        if len(output) >= limit:
            break
    return output
