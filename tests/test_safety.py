import unittest

from dreamnutri.content.safety import SafetyError, require_safe
from dreamnutri.schemas.evidence import Citation, NutritionClaim
from dreamnutri.schemas.request import IllustrationRequest


def citation(citation_id="cite1"):
    return Citation(citation_id=citation_id, text="Traceable fixture source")


def claim(text="A supported nutrition fact.", plain="A plain message.", claim_id="c1", citation_id="cite1"):
    return NutritionClaim(
        claim_id=claim_id,
        claim_text=text,
        plain_language_message=plain,
        evidence_source="fixture",
        citation_id=citation_id,
        population="general adults",
        evidence_strength="moderate",
        confidence=0.8,
        limitations=["Responses vary."],
    )


class SafetyTests(unittest.TestCase):
    def test_unsupported_treatment_claim_is_rejected(self):
        request = IllustrationRequest(
            topic="Nutrition",
            audience="general adults",
            nutrition_claims=[claim("This food cures diabetes.")],
            citations=[citation()],
        )
        with self.assertRaises(SafetyError):
            require_safe(request, request.nutrition_claims)

    def test_unsupported_number_is_rejected(self):
        request = IllustrationRequest(
            topic="Nutrition",
            audience="general adults",
            nutrition_claims=[claim("This food contains 30 g of fiber.")],
            citations=[citation()],
        )
        with self.assertRaises(SafetyError):
            require_safe(request, request.nutrition_claims)

    def test_plain_language_diagnosis_or_treatment_language_is_rejected(self):
        request = IllustrationRequest(
            topic="Nutrition",
            audience="general adults",
            nutrition_claims=[claim(plain="This picture provides a diagnosis and treatment plan.")],
            citations=[citation()],
        )
        with self.assertRaises(SafetyError):
            require_safe(request, request.nutrition_claims)

    def test_supplied_claims_require_traceable_citations(self):
        request = IllustrationRequest(
            topic="Nutrition",
            audience="general adults",
            nutrition_claims=[claim()],
        )
        with self.assertRaises(SafetyError):
            require_safe(request, request.nutrition_claims)

    def test_duplicate_claim_or_citation_ids_are_rejected(self):
        request = IllustrationRequest(
            topic="Nutrition",
            audience="general adults",
            nutrition_claims=[claim(claim_id="same"), claim(claim_id="same")],
            citations=[citation(), citation()],
        )
        with self.assertRaises(SafetyError):
            require_safe(request, request.nutrition_claims)
