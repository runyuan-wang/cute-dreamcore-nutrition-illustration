from pathlib import Path

from PIL import Image, ImageDraw

from dreamnutri.schemas.output import VisualSpec
from dreamnutri.providers.base import MOCK_PREVIEW_LABEL

from .safe_zones import pixel_box
from .typography import fit_text


def _draw_panel(draw, box):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=max(12, (y1 - y0) // 6), fill="#FFFDF8", outline="#DCCDEE", width=3)
    return x0 + (x1 - x0) // 20, y0 + (y1 - y0) // 12, x1 - (x1 - x0) // 20, y1 - (y1 - y0) // 12


def compose_final_image(raw_path: str | Path, output_path: str | Path, spec: VisualSpec, mock_preview: bool = False) -> dict:
    image = Image.open(raw_path).convert("RGBA")
    draw = ImageDraw.Draw(image)
    width, height = image.size
    title_zone = pixel_box(spec.composition.title_safe_zone, width, height)
    title_inner = _draw_panel(draw, title_zone)
    title = spec.topic if not spec.text_overlays else spec.text_overlays[0].text_en
    font, lines, title_overflow = fit_text(draw, title, title_inner[2] - title_inner[0], int((title_inner[3] - title_inner[1]) * 0.62), 2, max(30, width // 22), 16)
    y = title_inner[1]
    for line in lines:
        draw.text((title_inner[0], y), line, font=font, fill="#315B61")
        y += max(20, font.size + 6)
    subtitle_overlay = next((overlay for overlay in spec.text_overlays if overlay.kind == "subtitle"), None)
    subtitle_overflow = False
    if subtitle_overlay:
        subtitle_font, subtitle_lines, subtitle_overflow = fit_text(draw, subtitle_overlay.text_en, title_inner[2] - title_inner[0], int((title_inner[3] - title_inner[1]) * 0.30), 2, max(16, width // 42), 11)
        for line in subtitle_lines:
            draw.text((title_inner[0], y + 4), line, font=subtitle_font, fill="#59676B")
            y += max(16, subtitle_font.size + 4)
    caption_zone = pixel_box(spec.composition.caption_safe_zone, width, height)
    caption_inner = _draw_panel(draw, caption_zone)
    callouts = [overlay.text_en for overlay in spec.text_overlays if overlay.kind == "callout"]
    caption = " • ".join(callouts[:3]) or spec.educational_goal
    font, lines, caption_overflow = fit_text(draw, caption, caption_inner[2] - caption_inner[0], caption_inner[3] - caption_inner[1], 3, max(18, width // 38), 12)
    y = caption_inner[1]
    for line in lines:
        draw.text((caption_inner[0], y), line, font=font, fill="#59676B")
        y += max(16, font.size + 4)
    citation_ids = ", ".join(citation.citation_id for citation in spec.science_content.citations)
    if citation_ids:
        draw.text((30, height - 30), f"Sources: {citation_ids}", font=fit_text(draw, citation_ids, max(180, width // 4), 30, 1, 14, 10)[0], fill="#59676B")
    draw.text((width - max(190, width // 5), height - 30), "dreamnutri • MOCK" if mock_preview or spec.project_metadata.provider == "mock" else "dreamnutri", font=fit_text(draw, "dreamnutri", max(160, width // 5), 30, 1, 18, 10)[0], fill="#59676B")
    if mock_preview:
        banner_height = max(44, height // 22)
        draw.rectangle((0, 0, width, banner_height), fill="#EF8F7C")
        draw.text((18, max(8, banner_height // 5)), MOCK_PREVIEW_LABEL, font=fit_text(draw, MOCK_PREVIEW_LABEL, width - 36, banner_height - 8, 1, max(18, width // 42), 12)[0], fill="#FFFDF8")
    image.convert("RGB").save(output_path, format="PNG")
    return {"title_overflow": title_overflow, "subtitle_overflow": subtitle_overflow, "caption_overflow": caption_overflow, "dimensions": list(image.size), "text_overlay_status": "passed" if not (title_overflow or subtitle_overflow or caption_overflow) else "warning"}
