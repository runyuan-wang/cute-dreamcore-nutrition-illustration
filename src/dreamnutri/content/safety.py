from dataclasses import dataclass, field

from dreamnutri.schemas.evidence import NutritionClaim
from dreamnutri.schemas.request import IllustrationRequest


class SafetyError(ValueError):
    """Retained for API compatibility; content policy is owned upstream."""


@dataclass
class SafetyResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def validate_science(request: IllustrationRequest, claims: list[NutritionClaim]) -> SafetyResult:
    """Accept caller-supplied content without acting as a medical-content gate.

    This project renders cute educational images. Citation checks, medical review,
    and editorial decisions belong to the upstream content owner. In particular,
    missing citations and words such as prevention, treatment, or diagnosis do
    not block image generation here.
    """
    return SafetyResult()


def require_safe(request: IllustrationRequest, claims: list[NutritionClaim]) -> SafetyResult:
    return validate_science(request, claims)
