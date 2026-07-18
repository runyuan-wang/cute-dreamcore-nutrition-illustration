import hashlib
import json
from pathlib import Path

from PIL import Image

from dreamnutri.pipeline import generate_package
from dreamnutri.providers.fixture_provider import FixtureImageProvider
from dreamnutri.providers.text_planner import FakeTextPlanner
from dreamnutri.schemas.request import IllustrationRequest


REPO_ROOT = Path(__file__).parents[1]
AUTHENTIC = REPO_ROOT / "docs" / "images" / "authentic-demo-0718_1.png"


def test_arbitrary_topic_runs_two_validated_planning_stages(tmp_path):
    planner = FakeTextPlanner()
    request = IllustrationRequest(topic="How tea leaves become a daily ritual", audience="curious adults")
    out = generate_package(request, tmp_path / "topic", text_planner=planner)
    assert [call["stage"] for call in planner.calls] == [
        "teaching_priority_extraction",
        "structured_visual_spec_generation",
    ]
    spec = json.loads((out / "visual_spec.json").read_text(encoding="utf-8"))
    assert spec["planning"]["status"] == "planned"
    assert spec["planning"]["provider"] == "fake-text-planner"
    assert spec["planning"]["model"] == "offline-deterministic-text-planner-v1"
    assert "gpt" not in spec["planning"]["model"].lower()
    assert spec["planning"]["teaching_priorities"]
    assert spec["teaching_messages"]
    assert "Validated planner direction" in (out / "image_prompt.md").read_text(encoding="utf-8")


def test_provider_unavailable_does_not_silently_fabricate_gpt(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_TEXT_MODEL", raising=False)
    request = IllustrationRequest(topic="An arbitrary unavailable topic", audience="adults", provider="openai")
    out = generate_package(request, tmp_path / "unavailable")
    report = json.loads((out / "quality_report.json").read_text(encoding="utf-8"))
    assert report["planning"]["status"] == "provider_unavailable"
    assert report["planning"]["provider"] == "openai-compatible"
    assert "no GPT result was used" in " ".join(json.loads((out / "visual_spec.json").read_text(encoding="utf-8"))["quality_status"]["errors"])
    assert not (out / "illustration_raw.png").exists()


def test_language_selection_is_recorded_for_chinese_and_english(tmp_path):
    zh = IllustrationRequest(topic="Dietary Fiber and Gut Health", audience="adults", language="zh-CN")
    en = IllustrationRequest(topic="Dietary Fiber and Gut Health", audience="adults", language="en")
    zh_out = generate_package(zh, tmp_path / "zh")
    en_out = generate_package(en, tmp_path / "en")
    zh_overlay = json.loads((zh_out / "quality_report.json").read_text(encoding="utf-8"))["overlay"]
    en_overlay = json.loads((en_out / "quality_report.json").read_text(encoding="utf-8"))["overlay"]
    assert zh_overlay["language_selected"] == "zh-CN"
    assert any("纤维" in text for text in zh_overlay["selected_overlay_texts"])
    assert en_overlay["language_selected"] == "en"
    assert any("Fiber" in text for text in en_overlay["selected_overlay_texts"])
    assert zh_overlay["font_supports_cjk"] or zh_overlay["font_warning"]
    assert not zh_overlay["font_supports_cjk"] or zh_overlay["font_warning"] is None
    zh_lines = [line for group in zh_overlay["rendered_lines"].values() for line in group]
    assert any("and" in line for line in zh_lines)
    assert "a" not in zh_lines and "nd" not in zh_lines
    with Image.open(zh_out / "text_overlay_mock_preview.png") as image:
        image.verify()


def test_authentic_decoded_fixture_runs_raw_overlay_final_chain(tmp_path):
    request = IllustrationRequest(topic="Dietary Fiber and Gut Health", audience="general adults", provider="openai", model="fixture-model")
    out = generate_package(
        request,
        tmp_path / "fixture",
        text_planner=FakeTextPlanner(),
        image_provider=FixtureImageProvider(AUTHENTIC),
    )
    raw = out / "illustration_raw.png"
    final = out / "illustration_final.png"
    assert raw.read_bytes() == AUTHENTIC.read_bytes()
    assert hashlib.sha256(raw.read_bytes()).hexdigest() == "4d7f583ad897190720038f0f00775aae876593166d0fe2978aa0623be06feaf2"
    with Image.open(raw) as image:
        image.verify()
    with Image.open(final) as image:
        image.verify()
        assert image.size == (897, 1121)
    manifest = json.loads((out / "generation_manifest.json").read_text(encoding="utf-8"))
    assert manifest["artwork_status"] == "fixture_artwork_processed"
    assert manifest["provider_execution"] == "offline-png-fixture"
    assert manifest["real_artwork_paths"] == []
    assert manifest["fixture_artwork_paths"] == ["illustration_raw.png", "illustration_final.png"]
    assert manifest["provider_metadata"]["fixture_sha256"] == "4d7f583ad897190720038f0f00775aae876593166d0fe2978aa0623be06feaf2"
    quality = json.loads((out / "quality_report.json").read_text(encoding="utf-8"))
    assert quality["real_image_provider_required"] is True
    assert quality["overlay"]["provenance_label"] == "FIXTURE"


def test_readme_embeds_authentic_image_and_exact_hash():
    for name in ("README.md", "README.zh-CN.md"):
        text = (Path(__file__).parents[1] / name).read_text(encoding="utf-8")
        assert "docs/images/authentic-demo-0718_1.png" in text
        assert "4d7f583ad897190720038f0f00775aae876593166d0fe2978aa0623be06feaf2" in text
        assert "human-supplied" in text or "人类提供" in text
