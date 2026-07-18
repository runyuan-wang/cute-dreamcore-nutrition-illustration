import json
from pathlib import Path

from dreamnutri.pipeline import generate_package
from dreamnutri.providers.text_planner import FakeTextPlanner, OpenAITextPlanner
from dreamnutri.schemas.request import IllustrationRequest


class _Response:
    def __init__(self, payload, response_id):
        self.payload = payload
        self.response_id = response_id

    def raise_for_status(self):
        return None

    def json(self):
        return {
            "id": self.response_id,
            "choices": [{"message": {"content": json.dumps(self.payload, ensure_ascii=False)}}],
        }


def test_openai_planner_makes_two_language_explicit_validated_calls():
    payloads = []

    def post(url, *, headers, json, timeout):
        payloads.append(json)
        if len(payloads) == 1:
            return _Response(
                {
                    "topic": "Omega-3 basics",
                    "audience": "general adults",
                    "educational_goal": "温和解释核心概念",
                    "teaching_priorities": ["理解基本概念"],
                },
                "priority-response",
            )
        return _Response(
            {
                "topic": "Omega-3 basics",
                "title_en": "Omega-3 basics",
                "title_zh_cn": "Omega-3 基础知识",
                "subtitle_en": "A gentle introduction",
                "subtitle_zh_cn": "温和的入门介绍",
                "world_name": "The Floating Omega Garden",
                "hero_island_name": "Omega Learning Island",
                "teaching_messages": [
                    {
                        "message_id": "message_01",
                        "text_en": "Understand the basic idea",
                        "text_zh_cn": "理解基本概念",
                        "visual_metaphor": "a gentle river",
                    }
                ],
                "secondary_island_names": ["Everyday Example Island"],
                "visual_motifs": ["jade lantern spiral"],
                "image_prompt_guidance": "Keep one clean visual path.",
            },
            "visual-response",
        )

    request = IllustrationRequest(
        topic="Omega-3 basics", audience="general adults", language="zh-CN"
    )
    result = OpenAITextPlanner(api_key="test-only", post=post).plan(request, [], [])
    assert len(payloads) == 2
    assert all("temperature" not in item for item in payloads)
    assert all(json.loads(item["messages"][1]["content"])["language"] == "zh-CN" for item in payloads)
    assert result.metadata.response_ids == ["priority-response", "visual-response"]
    assert result.visual_spec.title_zh_cn == "Omega-3 基础知识"
    assert result.visual_spec.teaching_messages[0].text_en == "Understand the basic idea"


def test_arbitrary_chinese_overlay_and_unique_planned_motif_reach_outputs(tmp_path):
    def response_factory(stage, **kwargs):
        if stage == "teaching_priority_extraction":
            return {
                "topic": "Omega-3 basics",
                "audience": "general adults",
                "educational_goal": "温和解释核心概念",
                "teaching_priorities": ["理解基本概念"],
            }
        return {
            "topic": "Omega-3 basics",
            "title_en": "Omega-3 basics",
            "title_zh_cn": "Omega-3 基础知识",
            "subtitle_en": "A gentle introduction",
            "subtitle_zh_cn": "温和的入门介绍",
            "world_name": "The Floating Omega Garden",
            "hero_island_name": "Omega Learning Island",
            "teaching_messages": [
                {
                    "message_id": "message_01",
                    "text_en": "Understand the basic idea",
                    "text_zh_cn": "理解基本概念",
                    "visual_metaphor": "a gentle river",
                }
            ],
            "secondary_island_names": ["Everyday Example Island"],
            "visual_motifs": ["jade lantern spiral"],
            "image_prompt_guidance": "Keep one clean visual path.",
        }

    out = generate_package(
        IllustrationRequest(topic="Omega-3 basics", audience="general adults", language="zh-CN"),
        tmp_path,
        text_planner=FakeTextPlanner(response_factory=response_factory),
    )
    spec = json.loads((out / "visual_spec.json").read_text(encoding="utf-8"))
    report = json.loads((out / "quality_report.json").read_text(encoding="utf-8"))
    assert spec["text_overlays"][0]["text_zh_cn"] == "Omega-3 基础知识"
    assert spec["text_overlays"][2]["text_en"] == "Understand the basic idea"
    assert report["overlay"]["selected_overlay_texts"][:3] == [
        "Omega-3 基础知识",
        "温和的入门介绍",
        "理解基本概念",
    ]
    assert "jade lantern spiral" in (out / "image_prompt.md").read_text(encoding="utf-8")
    assert "jade lantern spiral" in spec["visual_world"]["decorative_elements"]
