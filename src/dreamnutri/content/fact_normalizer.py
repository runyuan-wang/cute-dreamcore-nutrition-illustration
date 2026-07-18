from copy import deepcopy
from typing import Any

from dreamnutri.schemas.evidence import NutritionClaim


CURATED_FIBER_CLAIMS = [
    NutritionClaim(
        claim_id="claim_01",
        claim_text="Dietary fiber is a type of carbohydrate that is not fully digested in the small intestine.",
        plain_language_message="Fiber travels farther through the digestive system than most digestible carbohydrates.",
        evidence_source="curated nutrition education",
        citation_id="c1",
        population="general adults",
        evidence_strength="established definition",
        confidence=0.98,
        limitations=["Different fibers have different properties."],
        allowed_visual_metaphors=["a gentle food path continuing toward a garden"],
        prohibited_visual_implications=["fiber is a living creature"],
    ),
    NutritionClaim(
        claim_id="claim_02",
        claim_text="Some fibers can be fermented by gut microorganisms, producing short-chain fatty acids among other products.",
        plain_language_message="Some fibers can be used by gut microorganisms in a fermentation process.",
        evidence_source="curated nutrition education",
        citation_id="c1",
        population="general adults",
        evidence_strength="supported mechanism",
        confidence=0.92,
        limitations=["Fermentation depends on fiber type and the individual gut ecosystem."],
        allowed_visual_metaphors=["friendly microbe sprites tending a fiber garden"],
        prohibited_visual_implications=["fiber literally turns into smiling microbes"],
    ),
    NutritionClaim(
        claim_id="claim_03",
        claim_text="Oats, beans, vegetables, fruit, corn, and sweet potato are examples of foods that can contribute dietary fiber.",
        plain_language_message="A varied pattern of plant foods can provide dietary fiber.",
        evidence_source="curated nutrition education",
        citation_id="c2",
        population="general adults",
        evidence_strength="food composition guidance",
        confidence=0.95,
        limitations=["Fiber content varies by food, portion, and preparation."],
        allowed_visual_metaphors=["small islands carrying colorful plant foods"],
        prohibited_visual_implications=["one food guarantees health"],
    ),
]


def normalize_claims(raw_claims: list[NutritionClaim] | list[dict[str, Any]], topic: str) -> list[NutritionClaim]:
    if raw_claims:
        return [claim if isinstance(claim, NutritionClaim) else NutritionClaim.model_validate(claim) for claim in raw_claims]
    if topic.strip().lower() in {"dietary fiber and gut health", "dietary fibre and gut health"}:
        return deepcopy(CURATED_FIBER_CLAIMS)
    return []


def normalize_food_examples(request_foods: list[str], claims: list[NutritionClaim]) -> list[str]:
    if request_foods:
        return list(dict.fromkeys(item.strip() for item in request_foods if item.strip()))
    text = " ".join(claim.claim_text for claim in claims).lower()
    known = ["oats", "beans", "vegetables", "fruit", "corn", "sweet potato"]
    return [item for item in known if item in text]


def citation_ids(claims: list[NutritionClaim]) -> set[str]:
    return {claim.citation_id for claim in claims}
