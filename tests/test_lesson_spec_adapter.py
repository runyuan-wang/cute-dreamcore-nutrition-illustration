import json
import tempfile
import unittest
from pathlib import Path

from dreamnutri.integrations.lesson_spec_adapter import illustration_request_from_lesson


class LessonAdapterTests(unittest.TestCase):
    def test_lesson_spec_import(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "lesson_spec.json"
            source.write_text(json.dumps({"title": "Fiber Basics", "audience": "general adults", "learning_objectives": ["Explain fiber gently"], "slides": [{"title": "Fiber Garden", "teaching_messages": ["Fiber supports a varied food pattern"], "claims": []}]}), encoding="utf-8")
            request = illustration_request_from_lesson(source, slide=1)
            self.assertEqual(request.topic, "Fiber Garden")
            self.assertEqual(request.use_case, "ppt_section")
            self.assertEqual(request.primary_messages, ["Fiber supports a varied food pattern"])
