import json
from pathlib import Path
from typing import Any

from dreamnutri.schemas.request import IllustrationRequest


def _first(data: dict[str, Any], *keys: str, default=None):
    for key in keys:
        if key in data and data[key] not in (None, ""):
            return data[key]
    return default


def _coerce_citations(items: list[Any]) -> list[dict[str, Any]]:
    result = []
    for index, item in enumerate(items, 1):
        if isinstance(item, str):
            result.append({"citation_id": f"lesson_citation_{index}", "text": item})
        else:
            result.append({
                "citation_id": str(_first(item, "citation_id", "id", "key", default=f"lesson_citation_{index}")),
                "text": str(_first(item, "text", "title", "citation", "reference", default="Lesson package citation")),
                "url": _first(item, "url", "doi", "link"),
            })
    return result


def _coerce_claims(items: list[Any], population: str) -> list[dict[str, Any]]:
    result = []
    for index, item in enumerate(items, 1):
        if isinstance(item, str):
            text = item
            item = {}
        else:
            text = str(_first(item, "claim_text", "text", "claim", "statement", default=""))
        if not text:
            continue
        citation_id = str(_first(item, "citation_id", "citation", "reference_id", default=f"lesson_citation_{index}"))
        result.append({
            "claim_id": str(_first(item, "claim_id", "id", default=f"lesson_claim_{index}")),
            "claim_text": text,
            "plain_language_message": str(_first(item, "plain_language_message", "plain_language", "message", default=text)),
            "evidence_source": str(_first(item, "evidence_source", "source", default="external lesson_spec.json")),
            "citation_id": citation_id,
            "population": str(_first(item, "population", "population_scope", default=population)),
            "evidence_strength": str(_first(item, "evidence_strength", "strength", default="not specified in lesson package")),
            "confidence": float(_first(item, "confidence", default=0.5)),
            "limitations": list(_first(item, "limitations", default=[])),
            "allowed_visual_metaphors": list(_first(item, "allowed_visual_metaphors", default=[])),
            "prohibited_visual_implications": list(_first(item, "prohibited_visual_implications", default=["literal anatomy", "unsupported medical implication"])),
        })
    return result


def illustration_request_from_lesson(path: str | Path, slide: int | None = None, use_case: str = "ppt_section", provider: str = "mock") -> IllustrationRequest:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    slides = data.get("slides") or data.get("slide_structure") or []
    selected = {}
    if slide is not None and slides:
        index = slide - 1
        if index < 0 or index >= len(slides):
            raise ValueError(f"slide {slide} is outside the lesson package")
        selected = slides[index]
    title = _first(selected, "title", "headline", default=_first(data, "title", "lesson_title", default="Nutrition lesson"))
    objectives = _first(selected, "learning_objectives", "objectives", default=_first(data, "learning_objectives", "objectives", default=[])) or []
    messages = _first(selected, "teaching_messages", "messages", "key_messages", default=objectives) or []
    population = _first(selected, "population_scope", "population", default="general adults")
    raw_claims = _first(selected, "nutrition_claims", "claims", default=data.get("nutrition_claims", data.get("claims", []))) or []
    raw_citations = _first(selected, "citations", "references", default=data.get("citations", data.get("references", []))) or []
    claims = _coerce_claims(raw_claims, population)
    citations = _coerce_citations(raw_citations)
    limitations = _first(selected, "limitations", default=data.get("limitations", [])) or []
    topic = _first(selected, "topic", default=title)
    audience = _first(selected, "audience", default=_first(data, "audience", default="general adults"))
    return IllustrationRequest(
        topic=topic,
        audience=audience,
        language=_first(selected, "language", default=_first(data, "language", default="en")),
        use_case=use_case,
        aspect_ratio="16:9" if use_case in {"ppt_cover", "ppt_section"} else "4:5",
        title=title,
        educational_goal="; ".join(objectives) if objectives else f"Explain {topic} accurately and gently.",
        primary_messages=[str(item) for item in messages[:3]],
        nutrition_claims=claims,
        population_scope=population,
        limitations=[str(item) for item in limitations],
        citations=citations,
        provider=provider,
        output_directory="outputs/from-lesson",
    )
