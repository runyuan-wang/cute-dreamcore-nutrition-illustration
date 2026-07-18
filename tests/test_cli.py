import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from dreamnutri.cli import main


class CliTests(unittest.TestCase):
    def test_from_lesson_mock_exits_cleanly_and_creates_no_final_artwork(self):
        fixture = Path(__file__).parent / "fixtures" / "lesson_spec.json"
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "lesson-output"
            argv = [
                "dreamnutri",
                "from-lesson",
                "--lesson-spec",
                str(fixture),
                "--slide",
                "2",
                "--use-case",
                "ppt_section",
                "--provider",
                "mock",
                "--output",
                str(output),
            ]
            with patch.object(sys, "argv", argv), redirect_stdout(io.StringIO()):
                return_code = main()
            self.assertEqual(return_code, 0)
            report = json.loads((output / "quality_report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["artwork_status"], "mock_layout_only")
            self.assertFalse((output / "illustration_raw.png").exists())
            self.assertFalse((output / "illustration_final.png").exists())
