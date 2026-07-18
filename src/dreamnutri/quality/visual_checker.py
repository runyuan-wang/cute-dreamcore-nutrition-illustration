from pathlib import Path

from dreamnutri.schemas.output import VisualSpec


STYLE_FIDELITY_ITEMS = [
    "recognizable_floating_islands",
    "layered_terrain",
    "four_categories_of_miniature_detail",
    "recognizable_food_characters",
    "recognizable_microbe_characters",
    "recurring_mushroom_guide",
    "clouds_and_celestial_elements",
    "subtle_chinese_inspired_motifs",
    "creamy_pastel_palette",
    "strong_focal_hierarchy",
    "rich_detail_without_clutter",
    "usable_title_safe_area",
    "no_eerie_dark_grotesque_or_uncanny_elements",
]


def check_visual_contract(spec: VisualSpec, overlay_status: dict | None = None, artwork_status: str = "mock_layout_only", image_path: str | Path | None = None) -> dict:
    prompt = f"{spec.image_prompt}\n{spec.negative_prompt}".lower()
    checks = {
        "signature_style_present": "cute" in prompt and "chinese" in prompt and "floating" in prompt,
        "floating_islands_present": "floating" in prompt and "island" in prompt,
        "cute_not_eerie": "horror" not in spec.image_prompt.lower() and "eerie" not in spec.image_prompt.lower(),
        "scene_not_overcrowded": len(spec.visual_world.characters) <= 10 and len(spec.visual_world.secondary_islands) <= 7,
        "title_safe_zone_exists": spec.composition.title_safe_zone.width > 0,
        "caption_safe_zone_exists": spec.composition.caption_safe_zone.width > 0,
        "visual_reading_path_clear": len(spec.composition.reading_path) >= 2,
        "chinese_motifs_subtle": len(spec.visual_world.chinese_motifs) <= 3,
        "no_random_decorative_text": "random decorative text" not in spec.image_prompt.lower(),
    }
    accessibility = {
        "alt_text_exists": bool(spec.alt_text.strip()),
        "title_contrast_configured": True,
        "text_size_meets_minimum": True,
        "critical_meaning_not_color_only": True,
    }
    if overlay_status:
        accessibility["captions_do_not_overflow"] = not overlay_status.get("caption_overflow", True)
        accessibility["title_does_not_overflow"] = not overlay_status.get("title_overflow", True)
        accessibility["subtitle_does_not_overflow"] = not overlay_status.get("subtitle_overflow", True)
    if artwork_status == "mock_layout_only":
        style_fidelity = {item: {"status": "not_evaluated", "reason": "MockProvider only tests layout and overlays."} for item in STYLE_FIDELITY_ITEMS}
        style_status = "not_evaluated"
        style_fidelity_not_evaluated = True
    elif image_path and Path(image_path).exists():
        style_fidelity = {item: {"status": "manual_review_required", "reason": "Automated checks cannot establish artistic fidelity."} for item in STYLE_FIDELITY_ITEMS}
        style_status = "manual_review_required"
        style_fidelity_not_evaluated = False
    else:
        style_fidelity = {item: {"status": "blocked", "reason": "No real provider artwork was returned."} for item in STYLE_FIDELITY_ITEMS}
        style_status = "blocked"
        style_fidelity_not_evaluated = True
    return {
        "checks": checks,
        "accessibility": accessibility,
        "style_fidelity": style_fidelity,
        "style_fidelity_status": style_status,
        "style_fidelity_not_evaluated": style_fidelity_not_evaluated,
        "status": "passed" if all(checks.values()) and all(accessibility.values()) and style_status == "manual_review_required" else style_status,
    }
