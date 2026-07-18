import re
from dataclasses import dataclass, field

from dreamnutri.schemas.evidence import NutritionClaim
from dreamnutri.schemas.request import IllustrationRequest


class SafetyError(ValueError):
    pass


UNSAFE_TERMS = re.compile(
    r"\b(?:"
    r"cure(?:s|d|ing)?|"
    r"treat(?:s|ed|ing|ment|ments)?|"
    r"prevent(?:s|ed|ing|ion)?|"
    r"reverse(?:s|d|ing)?|"
    r"detox(?:es|ed|ing)?|"
    r"guarantee(?:s|d|ing)?|"
    r"prescrib(?:e|es|ed|ing)|prescription(?:s)?|"
    r"diagnos(?:e|es|ed|ing|is|tic|tics)"
    r")\b|治愈|治疗|预防|逆转|排毒|保证|诊断|处方",
    re.I,
)
NUMBER_PATTERN = re.compile(r"(?<![A-Za-z])\d+(?:\.\d+)?\s*(?:%|g|mg|kcal|毫克|克|%)?", re.I)


@dataclass
class SafetyResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def validate_science(request: IllustrationRequest, claims: list[NutritionClaim]) -> SafetyResult:
    result = SafetyResult()
    if len(request.primary_messages) > 3:
        result.errors.append("More than 3 primary messages were requested.")
    if not claims:
        result.warnings.append("No supplied or curated claims; package is concept-only and must not imply health effects.")
    claim_ids = [claim.claim_id for claim in claims]
    citation_id_list = [citation.citation_id for citation in request.citations]
    citation_ids = set(citation_id_list)
    if len(set(claim_ids)) != len(claim_ids):
        result.errors.append("Claim IDs must be unique.")
    if len(citation_ids) != len(citation_id_list):
        result.errors.append("Citation IDs must be unique.")
    if claims and not request.citations:
        result.errors.append("Claims require a traceable citation list.")
    for claim in claims:
        if not claim.evidence_source.strip():
            result.errors.append(f"{claim.claim_id} has no evidence source.")
        if request.citations and claim.citation_id not in citation_ids:
            result.errors.append(f"{claim.claim_id} cites unknown citation {claim.citation_id}.")
        for field_name, text in (("claim", claim.claim_text), ("plain-language message", claim.plain_language_message)):
            if UNSAFE_TERMS.search(text):
                result.errors.append(f"{claim.claim_id} contains diagnosis/treatment/prevention language in its {field_name}.")
            if NUMBER_PATTERN.search(text):
                result.errors.append(f"{claim.claim_id} contains an unsupported number in its {field_name}; supply explicit evidence handling.")
        if not claim.limitations:
            result.warnings.append(f"{claim.claim_id} has no claim-specific limitation.")
    for message in request.primary_messages:
        if UNSAFE_TERMS.search(message):
            result.errors.append("A primary message contains a treatment/prevention promise.")
        if NUMBER_PATTERN.search(message):
            result.errors.append("A primary message contains a number without a supplied claim-supported numeric context.")
    if not request.limitations:
        result.warnings.append("No package-level limitations supplied; preserve uncertainty in the accompanying report.")
    if request.population_scope.strip().lower() not in {claim.population.strip().lower() for claim in claims} and claims:
        result.warnings.append("Request population scope differs from at least one claim population; retain the narrowest scope.")
    return result


def require_safe(request: IllustrationRequest, claims: list[NutritionClaim]) -> SafetyResult:
    result = validate_science(request, claims)
    if result.errors:
        raise SafetyError("; ".join(result.errors))
    return result
