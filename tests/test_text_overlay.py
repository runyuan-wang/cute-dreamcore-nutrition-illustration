import tempfile
import unittest
from pathlib import Path

from PIL import Image

from dreamnutri.pipeline import generate_package
from dreamnutri.schemas.request import IllustrationRequest


class TextOverlayTests(unittest.TestCase):
    def test_text_overlay_wraps_and_exports_png(self):
        with tempfile.TemporaryDirectory() as directory:
            request = IllustrationRequest(topic="Dietary Fiber and Gut Health", audience="general adults", title="Dietary Fiber & Gut Health")
            out = generate_package(request, Path(directory) / "fiber")
            with Image.open(out / "text_overlay_mock_preview.png") as image:
                self.assertEqual(image.size, (1080, 1350))
            self.assertIn("caption_overflow", (out / "quality_report.json").read_text(encoding="utf-8"))
