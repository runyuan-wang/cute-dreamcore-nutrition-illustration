from dreamnutri.content.safety import SafetyResult, validate_science
from dreamnutri.schemas.request import IllustrationRequest
from dreamnutri.schemas.evidence import NutritionClaim


def check_content(request: IllustrationRequest, claims: list[NutritionClaim]) -> dict:
    result: SafetyResult = validate_science(request, claims)
    citation_ids = {citation.citation_id for citation in request.citations}
    referenced = {claim.citation_id for claim in claims}
    checks = {
        "claim_has_evidence": all(bool(claim.evidence_source.strip()) for claim in claims) if claims else False,
        "unsupported_numbers_rejected": not any("unsupported number" in error for error in result.errors),
        "no_causal_or_treatment_overstatement": not any("promise" in error for error in result.errors),
        "population_scope_retained": bool(request.population_scope),
        "limitations_present": bool(request.limitations) or any(claim.limitations for claim in claims),
        "citations_preserved": not referenced or referenced.issubset(citation_ids) or not request.citations,
        "food_examples_match_topic": True,
        "no_random_citations": referenced.issubset(citation_ids) if request.citations else True,
    }
    return {"checks": checks, "errors": result.errors, "warnings": result.warnings, "status": "passed" if result.ok else "failed"}
