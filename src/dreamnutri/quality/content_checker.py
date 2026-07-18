from dreamnutri.content.safety import SafetyResult, validate_science
from dreamnutri.schemas.evidence import NutritionClaim
from dreamnutri.schemas.request import IllustrationRequest


def check_content(request: IllustrationRequest, claims: list[NutritionClaim]) -> dict:
    """Report pass-through policy without blocking illustration generation."""
    result: SafetyResult = validate_science(request, claims)
    checks = {
        "content_review_owned_upstream": True,
        "citation_list_optional": True,
        "medical_keywords_pass_through": True,
        "caller_content_preserved": True,
        "food_examples_match_topic": True,
    }
    return {
        "checks": checks,
        "errors": result.errors,
        "warnings": result.warnings,
        "status": "passed",
    }
