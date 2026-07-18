import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from dreamnutri.pipeline import generate_package
from dreamnutri.schemas.request import IllustrationRequest


class ProviderSemanticsTests(unittest.TestCase):
    def test_real_provider_failure_does_not_promote_mock_to_final(self):
        request = IllustrationRequest(topic="Dietary Fiber and Gut Health", audience="general adults", provider="openai")
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {"OPENAI_API_KEY": "", "OPENAI_IMAGE_MODEL": ""}, clear=False):
            out = generate_package(request, Path(directory) / "unavailable")
            self.assertTrue((out / "layout_mock_preview.png").exists())
            self.assertTrue((out / "text_overlay_mock_preview.png").exists())
            self.assertFalse((out / "illustration_raw.png").exists())
            self.assertFalse((out / "illustration_final.png").exists())
            report = json.loads((out / "quality_report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["artwork_status"], "provider_unavailable")
            self.assertTrue(report["real_image_provider_required"])
