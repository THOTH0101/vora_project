import re
from bisect import bisect_right
from typing import TypedDict


PII_ENTITY_LABELS = frozenset(
    {"PERSON", "PER", "EMAIL_ADDRESS", "PHONE_NUMBER", "NIGERIAN_PHONE_NUMBER"}
)
REDACTION_MARKER_RE = re.compile(
    r"<(?:PERSON|EMAIL_ADDRESS|PHONE_NUMBER|NIGERIAN_PHONE_NUMBER)>"
)
PAGE_MARKER_RE = re.compile(r"(?m)^\[PAGE ([1-9]\d*)\][ \t]*$")


class EntityHint(TypedDict):
    text: str
    label: str
    page: int | None


def sanitize_entity_hints(entities: list[dict], redacted_text: str) -> list[EntityHint]:
    """Send only non-PII entity values present in the redacted document."""
    hints = []
    seen = set()
    pages = {int(match[1]) for match in PAGE_MARKER_RE.finditer(redacted_text)}
    for entity in entities:
        text, label = entity.get("text"), entity.get("label")
        if not isinstance(text, str) or not text.strip() or not isinstance(label, str):
            continue
        if label.upper() in PII_ENTITY_LABELS or REDACTION_MARKER_RE.search(text):
            continue
        if text not in redacted_text:
            continue
        page = entity.get("page")
        if type(page) is not int or page not in pages:
            page = None
        key = (text, label, page)
        if key not in seen:
            hints.append(EntityHint(text=text, label=label, page=page))
            seen.add(key)
    return hints


def build_entity_hints(
    original_text: str,
    redacted_text: str,
    entities: list[dict],
    pii: list[dict],
) -> list[EntityHint]:
    """Drop entities overlapping PII and map original offsets to source pages."""
    markers = list(PAGE_MARKER_RE.finditer(original_text))
    page_starts = [marker.start() for marker in markers]
    safe_entities = []
    for entity in entities:
        start, end = entity.get("start"), entity.get("end")
        if type(start) is not int or type(end) is not int:
            continue
        if not 0 <= start < end <= len(original_text):
            continue
        if original_text[start:end] != entity.get("text"):
            continue
        if any(start < finding["end"] and end > finding["start"] for finding in pii):
            continue
        page_index = bisect_right(page_starts, start) - 1
        page = int(markers[page_index][1]) if page_index >= 0 else None
        safe_entities.append(
            {"text": entity["text"], "label": entity.get("label"), "page": page}
        )
    return sanitize_entity_hints(safe_entities, redacted_text)
