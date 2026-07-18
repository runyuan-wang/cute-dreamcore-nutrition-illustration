import tempfile
import unittest
from pathlib import Path

from dreamnutri.content.safety import require_safe
from dreamnutri.pipeline import generate_package, validate_visual_spec
from dreamnutri.schemas.evidence import NutritionClaim
from dreamnutri.schemas.request import IllustrationRequest


def claim(text="A nutrition fact.", plain="A plain message."):
    return NutritionClaim(
        claim_id="c1",
        claim_text=text,
        plain_language_message=plain,
        evidence_source="caller supplied",
        citation_id="not-listed",
        population="general adults",
        evidence_strength="caller supplied",
        confidence=0.5,
        limitations=[],
    )


class ContentPassThroughTests(unittest.TestCase):
    def test_missing_citation_list_does_not_block(self):
        request = IllustrationRequest(
            topic="Nutrition",
            audience="general adults",
            nutrition_claims=[claim()],
            citations=[],
        )
        self.assertTrue(require_safe(request, request.nutrition_claims).ok)

    def test_medical_words_and_numbers_do_not_block(self):
        request = IllustrationRequest(
            topic="Nutrition education",
            audience="general adults",
            nutrition_claims=[claim(
                "A lesson may discuss prevention, treatment, diagnosis, and 30 g examples.",
                "This educational picture mentions diagnosis and treatment.",
            )],
            citations=[],
        )
        self.assertTrue(require_safe(request, request.nutrition_claims).ok)

    def test_pipeline_generates_without_citations_or_keyword_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            request = IllustrationRequest(
                topic="Prevention, treatment, and diagnosis education",
                audience="general adults",
                primary_messages=["Explain prevention, treatment, and diagnosis in a cute science image."],
                citations=[],
                output_directory=directory,
            )
            out = generate_package(request, Path(directory) / "pass-through")
            spec = validate_visual_spec(out / "visual_spec.json")
            self.assertEqual(spec.science_content.citations, [])
            self.assertTrue((out / "layout_mock_preview.png").exists())
            self.assertFalse((out / "illustration_final.png").exists())
