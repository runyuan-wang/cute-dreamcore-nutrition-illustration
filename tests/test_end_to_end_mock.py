import json
import tempfile
import unittest
from pathlib import Path

from dreamnutri.pipeline import generate_package, validate_visual_spec
from dreamnutri.schemas.request import IllustrationRequest


EXPECTED = {
    "request.json", "normalized_facts.json", "teaching_messages.json", "visual_spec.json", "visual_brief.md",
    "image_prompt.md", "negative_prompt.md", "caption.en.md", "caption.zh-CN.md", "alt_text.en.md", "alt_text.zh-CN.md",
    "citations.md", "quality_report.json", "quality_report.md", "generation_manifest.json", "layout_mock_preview.png", "text_overlay_mock_preview.png", "comparison_contact_sheet.png",
}


class EndToEndTests(unittest.TestCase):
    def test_complete_offline_example_run(self):
        with tempfile.TemporaryDirectory() as directory:
            request = IllustrationRequest(topic="Dietary Fiber and Gut Health", audience="general adults", output_directory=directory)
            out = generate_package(request, Path(directory) / "dietary-fiber")
            self.assertTrue(EXPECTED.issubset({path.name for path in out.iterdir()}))
            spec = validate_visual_spec(out / "visual_spec.json")
            self.assertEqual(spec.project_metadata.provider, "mock")
            self.assertEqual(spec.project_metadata.version, "0.2.0")
            self.assertEqual([item.citation_id for item in spec.science_content.citations], ["c1", "c2"])
            citations_text = (out / "citations.md").read_text(encoding="utf-8")
            self.assertIn("s41575-019-0153-8", citations_text)
            self.assertIn("dietaryguidelines.gov", citations_text)
            self.assertFalse((out / "illustration_raw.png").exists())
            self.assertFalse((out / "illustration_final.png").exists())
            manifest = json.loads((out / "generation_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["provider"], "mock")
            self.assertEqual(manifest["input_claim_ids"], ["claim_01", "claim_02", "claim_03"])
            report = json.loads((out / "quality_report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["artwork_status"], "mock_layout_only")
            self.assertTrue(report["style_fidelity_not_evaluated"])
            self.assertTrue(report["real_image_provider_required"])
