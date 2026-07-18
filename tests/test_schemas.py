import unittest
from pydantic import ValidationError

from dreamnutri.schemas.evidence import NutritionClaim
from dreamnutri.schemas.request import IllustrationRequest
from dreamnutri.schemas.output import VisualSpec


class SchemaTests(unittest.TestCase):
    def test_request_defaults_express_signature_style(self):
        request = IllustrationRequest(topic="Dietary Fiber and Gut Health", audience="general adults")
        self.assertEqual(request.style_preset, "cute_chinese_dreamcore_floating_islands")
        self.assertEqual(request.cuteness_level, 5)
        self.assertTrue(request.include_mushrooms)
        self.assertEqual((request.width, request.height), (1080, 1350))


    def test_claim_requires_evidence_fields(self):
        with self.assertRaises(ValidationError):
            NutritionClaim(claim_id="x", claim_text="A claim", plain_language_message="A message")


    def test_visual_spec_rejects_unknown_fields(self):
        with self.assertRaises(ValidationError):
            VisualSpec.model_validate({"unexpected": True})
