import json
import re
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

from dreamnutri.content.fact_normalizer import normalize_claims, normalize_food_examples
from dreamnutri.content.safety import require_safe
from dreamnutri.content.teaching_messages import build_teaching_messages
from dreamnutri.providers.base import ProviderResult
from dreamnutri.providers.mock_provider import MockProvider
from dreamnutri.quality.content_checker import check_content
from dreamnutri.quality.report import markdown_report
from dreamnutri.quality.visual_checker import check_visual_contract
from dreamnutri.render.compositor import compose_final_image
from dreamnutri.render.contact_sheet import create_comparison_contact_sheet
from dreamnutri.render.export import write_json, write_text
from dreamnutri.render.safe_zones import zones_for
from dreamnutri.schemas.output import Composition, ProjectMetadata, QualityStatus, ScienceContent, TextOverlay, VisualSpec
from dreamnutri.schemas.request import IllustrationRequest
from dreamnutri.style.prompt_builder import build_image_prompt, build_negative_prompt
from dreamnutri.style.world_builder import build_visual_world


def _slug(text: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return value or "nutrition-illustration"


def _chinese_text(text: str, topic: str) -> str:
    if "fiber" in topic.lower() or "fibre" in topic.lower():
        translations = {
            "Dietary Fiber and Gut Health": "膳食纤维与肠道健康",
            "Dietary Fiber & Gut Health": "膳食纤维与肠道健康",
            "Fiber travels farther through the digestive system than most digestible carbohydrates.": "膳食纤维不会像大多数可消化碳水那样在小肠中被完全消化。",
            "Some fibers can be used by gut microorganisms in a fermentation process.": "一些膳食纤维可以被肠道微生物利用并参与发酵过程。",
            "A varied pattern of plant foods can provide dietary fiber.": "多样化的植物性食物可以提供膳食纤维。",
        }
        return translations.get(text, text)
    return text


def _alt_text(topic: str, world, messages, language: str) -> str:
    islands = ", ".join(island.name for island in world.secondary_islands[:5]) or "small food islands"
    message_text = "; ".join(message.headline for message in messages[:3])
    return f"A cute Chinese dreamcore floating-island science illustration about {topic}. A central symbolic nutrition ecosystem island is connected by cloud paths to {islands}; friendly food residents, microbe sprites, a mushroom guide, flowers, stars, and subtle garden motifs create a warm educational world. Key messages: {message_text}. The scenery is symbolic, not literal anatomy."


def _alt_text_zh_cn(topic: str, world, messages) -> str:
    islands = "、".join(island.name for island in world.secondary_islands[:5]) or "小型食物浮岛"
    message_text = "；".join(_chinese_text(message.headline, topic) for message in messages[:3]) or "用温和方式解释一个营养概念"
    return f"一张关于{_chinese_text(topic, topic)}的可爱中国梦核浮空岛科学插画。中央是象征性的营养生态系统岛屿，云朵路径连接着{islands}；友好的食物居民、微生物精灵、小蘑菇向导、花朵、星星和含蓄的园林元素共同构成温暖的教育世界。核心信息：{message_text}。画面是视觉隐喻，不是真实解剖。"


def _provider_for(name: str):
    if name == "mock":
        return MockProvider()
    if name == "openai":
        from dreamnutri.providers.openai_image_provider import OpenAIImageProvider
        return OpenAIImageProvider()
    raise ValueError(f"Unsupported provider: {name}")


def _request_dump(request: IllustrationRequest) -> dict:
    return request.model_dump(mode="json")


def _write_captions(out: Path, spec: VisualSpec) -> None:
    title_en = spec.text_overlays[0].text_en if spec.text_overlays else spec.topic
    title_zh = spec.text_overlays[0].text_zh_cn if spec.text_overlays else spec.topic
    callouts_en = [item.text_en for item in spec.text_overlays if item.kind == "callout"]
    callouts_zh = [item.text_zh_cn for item in spec.text_overlays if item.kind == "callout"]
    write_text(out / "caption.en.md", "# " + title_en + "\n\n" + "\n".join(f"- {text}" for text in callouts_en) + "\n\n" + "_Science communication only; not individualized medical advice._")
    write_text(out / "caption.zh-CN.md", "# " + title_zh + "\n\n" + "\n".join(f"- {text}" for text in callouts_zh) + "\n\n" + "_仅用于科学传播，不构成个体化医疗建议。_")
    write_text(out / "alt_text.en.md", spec.alt_text)
    write_text(out / "alt_text.zh-CN.md", spec.alt_text_zh_cn)
    citations = [f"- {citation.citation_id}: {citation.text}" + (f" — {citation.url}" if citation.url else "") for citation in spec.science_content.citations]
    write_text(out / "citations.md", "\n".join(citations) if citations else "No citations were supplied; image generation still proceeds.")


def _visual_brief(spec: VisualSpec) -> str:
    world = spec.visual_world
    lines = [f"# {world.world_name}", "", f"Topic: {spec.topic}", f"Audience: {spec.audience}", "", "## Teaching messages", ""]
    lines.extend(f"- {message.headline} — visual metaphor: {message.visual_metaphor}" for message in spec.teaching_messages)
    lines += ["", "## World", "", f"Hero island: {world.hero_island.name} ({world.hero_island.role})", "Secondary islands: " + ", ".join(item.name for item in world.secondary_islands), "Characters: " + ", ".join(item.name for item in world.characters), "", "This world is symbolic and not literal anatomy."]
    return "\n".join(lines)


def generate_package(request: IllustrationRequest, output_dir: str | Path | None = None) -> Path:
    claims = normalize_claims(request.nutrition_claims, request.topic)
    safety = require_safe(request, claims)
    foods = normalize_food_examples(request.food_examples, claims)
    messages = build_teaching_messages(request.primary_messages, claims)
    title_zone, caption_zone = zones_for(request)
    world = build_visual_world(request, foods)
    composition = Composition(
        aspect_ratio=request.aspect_ratio,
        title_safe_zone=title_zone,
        caption_safe_zone=caption_zone,
        visual_focus="Follow the gentle path from plant-food islands to the central symbolic ecosystem island.",
        reading_path=["food examples", "cloud paths", "hero nutrition ecosystem", "caption area"],
    )
    overlays = [
        TextOverlay(overlay_id="title", kind="title", text_en=request.title or request.topic, text_zh_cn=_chinese_text(request.title or request.topic, request.topic), safe_zone=title_zone, max_lines=2),
        TextOverlay(overlay_id="subtitle", kind="subtitle", text_en=request.subtitle or request.educational_goal, text_zh_cn=_chinese_text(request.subtitle or request.educational_goal, request.topic), safe_zone=title_zone, max_lines=2),
    ]
    for index, message in enumerate(messages, 1):
        overlays.append(TextOverlay(overlay_id=f"callout_{index:02d}", kind="callout", text_en=message.headline, text_zh_cn=_chinese_text(message.headline, request.topic), safe_zone=caption_zone, max_lines=2))
    image_prompt = build_image_prompt(request.model_copy(update={"food_examples": foods}), claims, world, composition)
    negative_prompt = build_negative_prompt()
    project_metadata = ProjectMetadata(provider=request.provider, model=request.model)
    limitations = list(dict.fromkeys(request.limitations + [limitation for claim in claims for limitation in claim.limitations]))
    spec = VisualSpec(
        project_metadata=project_metadata,
        topic=request.topic,
        audience=request.audience,
        language=request.language,
        educational_goal=request.educational_goal,
        science_content=ScienceContent(claims=claims, limitations=limitations, citations=request.citations),
        teaching_messages=messages,
        visual_world=world,
        composition=composition,
        image_prompt=image_prompt,
        negative_prompt=negative_prompt,
        text_overlays=overlays,
        alt_text=_alt_text(request.topic, world, messages, "en"),
        alt_text_zh_cn=_alt_text_zh_cn(request.topic, world, messages),
        quality_status=QualityStatus(status="planned", warnings=safety.warnings, errors=safety.errors),
    )
    if output_dir is None:
        base = Path(request.output_directory)
        if base.name == "outputs" or str(base) == "outputs":
            base = base / f"{_slug(request.topic)}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
        out = base
    else:
        out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    for stale_path in (out / "illustration_raw.png", out / "illustration_final.png"):
        if stale_path.exists():
            stale_path.unlink()
    content_report = check_content(request, claims)

    # These previews are deliberately separate from real artwork. They make the
    # layout/overlay chain testable without allowing mock output to pass as art.
    mock_provider = MockProvider()
    layout_mock_path = out / "layout_mock_preview.png"
    mock_result = mock_provider.generate(spec.image_prompt, spec.negative_prompt, request.width, request.height, layout_mock_path, request.seed, request.model)
    text_overlay_mock_path = out / "text_overlay_mock_preview.png"
    mock_overlay_status = compose_final_image(layout_mock_path, text_overlay_mock_path, spec, mock_preview=True) if request.text_overlay_mode == "programmatic" else {"text_overlay_status": "skipped", "title_overflow": False, "subtitle_overflow": False, "caption_overflow": False, "dimensions": [request.width, request.height]}

    provider_result: ProviderResult | None = None
    provider_error: str | None = None
    raw_path = out / "illustration_raw.png"
    final_path = out / "illustration_final.png"
    if request.provider == "mock":
        artwork_status = "mock_layout_only"
        primary_overlay_status = mock_overlay_status
        actual_dimensions = list(mock_result.returned_dimensions or (request.width, request.height))
    else:
        provider = _provider_for(request.provider)
        try:
            provider_result = provider.generate(spec.image_prompt, spec.negative_prompt, request.width, request.height, raw_path, request.seed, request.model)
            with Image.open(raw_path) as returned_image:
                actual_dimensions = list(returned_image.size)
            if not provider_result.returned_dimensions:
                provider_result.returned_dimensions = tuple(actual_dimensions)
            if request.text_overlay_mode == "programmatic":
                primary_overlay_status = compose_final_image(raw_path, final_path, spec)
            else:
                primary_overlay_status = {"text_overlay_status": "skipped", "title_overflow": False, "subtitle_overflow": False, "caption_overflow": False, "dimensions": actual_dimensions}
            artwork_status = "real_artwork_generated"
        except Exception as exc:
            # This is an honest stop: the mock is only a diagnostic preview and
            # is never assigned to illustration_raw.png or illustration_final.png.
            provider_error = str(exc)
            artwork_status = "provider_unavailable"
            primary_overlay_status = mock_overlay_status
            actual_dimensions = list(mock_result.returned_dimensions or (request.width, request.height))

    visual_report = check_visual_contract(
        spec,
        primary_overlay_status,
        artwork_status=artwork_status,
        image_path=raw_path if raw_path.exists() else None,
    )
    final_status = "warning"
    if content_report["status"] != "passed":
        final_status = "failed"
    spec.quality_status = QualityStatus(status=final_status, warnings=content_report["warnings"], errors=content_report["errors"])
    manifest = {
        "provider": request.provider,
        "requested_model": provider_result.requested_model if provider_result else request.model,
        "actual_model_when_available": provider_result.actual_model if provider_result else None,
        "response_id_when_available": provider_result.response_id if provider_result else None,
        "generation_timestamp": datetime.now(timezone.utc).isoformat(),
        "prompt_version": "0.1.0",
        "style_system_version": "0.1.0",
        "input_claim_ids": [claim.claim_id for claim in claims],
        "citation_ids": [citation.citation_id for citation in request.citations],
        "requested_image_dimensions": [request.width, request.height],
        "returned_image_dimensions": actual_dimensions,
        "seed_when_available": provider_result.seed if provider_result else request.seed,
        "content_validation_status": content_report["status"],
        "style_validation_status": visual_report["status"],
        "text_overlay_status": primary_overlay_status.get("text_overlay_status", "unknown"),
        "artwork_status": artwork_status,
        "provider_error": provider_error,
        "mock_preview_paths": ["layout_mock_preview.png", "text_overlay_mock_preview.png"],
        "real_artwork_paths": ["illustration_raw.png", "illustration_final.png"] if artwork_status == "real_artwork_generated" else [],
    }
    write_json(out / "request.json", _request_dump(request))
    write_json(out / "normalized_facts.json", {"claims": [claim.model_dump(mode="json") for claim in claims], "food_examples": foods})
    write_json(out / "teaching_messages.json", [message.model_dump(mode="json") for message in messages])
    write_json(out / "visual_spec.json", spec.model_dump(mode="json"))
    write_text(out / "visual_brief.md", _visual_brief(spec))
    write_text(out / "image_prompt.md", spec.image_prompt)
    write_text(out / "negative_prompt.md", spec.negative_prompt)
    _write_captions(out, spec)
    create_comparison_contact_sheet(out)
    quality_report = {
        "artwork_status": artwork_status,
        "style_fidelity_not_evaluated": visual_report["style_fidelity_not_evaluated"],
        "real_image_provider_required": artwork_status != "real_artwork_generated",
        "content": content_report,
        "visual": visual_report,
        "overlay": primary_overlay_status,
        "mock_overlay": mock_overlay_status,
        "provider_error": provider_error,
    }
    write_json(out / "quality_report.json", quality_report)
    write_text(out / "quality_report.md", markdown_report(content_report, visual_report, request.provider, str(out), artwork_status, provider_error))
    write_json(out / "generation_manifest.json", manifest)
    return out


def finalize_external_real_artwork(output_dir: str | Path, provider_execution: str = "external_real_image_provider", actual_model: str | None = None, response_id: str | None = None) -> Path:
    """Finalize a real image returned outside the Python provider call.

    This keeps the raw artwork, overlays, contact sheet, manifest, and report
    consistent while recording the execution route explicitly.
    """
    out = Path(output_dir)
    spec = validate_visual_spec(out / "visual_spec.json")
    request = IllustrationRequest.model_validate_json((out / "request.json").read_text(encoding="utf-8"))
    raw_path = out / "illustration_raw.png"
    if not raw_path.exists():
        raise FileNotFoundError("A real illustration_raw.png is required before finalization.")
    with Image.open(raw_path) as image:
        returned_dimensions = list(image.size)
    final_path = out / "illustration_final.png"
    overlay_status = compose_final_image(raw_path, final_path, spec) if request.text_overlay_mode == "programmatic" else {"text_overlay_status": "skipped", "title_overflow": False, "subtitle_overflow": False, "caption_overflow": False, "dimensions": returned_dimensions}
    content_report = check_content(request, spec.science_content.claims)
    visual_report = check_visual_contract(spec, overlay_status, artwork_status="real_artwork_generated", image_path=raw_path)
    spec.quality_status = QualityStatus(status="warning", warnings=content_report["warnings"] + ["Manual artistic review remains required."], errors=content_report["errors"])
    manifest_path = out / "generation_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    manifest.update({
        "provider": request.provider,
        "provider_execution": provider_execution,
        "requested_model": request.model,
        "actual_model_when_available": actual_model,
        "response_id_when_available": response_id,
        "returned_image_dimensions": returned_dimensions,
        "content_validation_status": content_report["status"],
        "style_validation_status": visual_report["status"],
        "text_overlay_status": overlay_status.get("text_overlay_status", "unknown"),
        "artwork_status": "real_artwork_generated",
        "provider_error": None,
        "real_artwork_paths": ["illustration_raw.png", "illustration_final.png"],
    })
    create_comparison_contact_sheet(out)
    quality_report = {
        "artwork_status": "real_artwork_generated",
        "style_fidelity_not_evaluated": False,
        "real_image_provider_required": False,
        "manual_style_review_required": True,
        "content": content_report,
        "visual": visual_report,
        "overlay": overlay_status,
        "provider_error": None,
    }
    write_json(out / "visual_spec.json", spec.model_dump(mode="json"))
    write_json(out / "generation_manifest.json", manifest)
    write_json(out / "quality_report.json", quality_report)
    write_text(out / "quality_report.md", markdown_report(content_report, visual_report, request.provider, str(out), "real_artwork_generated"))
    return out


def validate_visual_spec(path: str | Path) -> VisualSpec:
    return VisualSpec.model_validate_json(Path(path).read_text(encoding="utf-8"))
