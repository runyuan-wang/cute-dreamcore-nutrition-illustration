import os
import re
from pathlib import Path

from PIL import ImageFont


FONT_CANDIDATES = [
    os.getenv("DREAMNUTRI_FONT_PATH", ""),
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/System/Library/Fonts/Supplemental/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]

CJK_FONT_NAME_TOKENS = ("cjk", "unicode", "noto", "sourcehan", "source-han")


def font_metadata(text: str = "", size: int = 16) -> dict:
    """Select a CJK-capable candidate when needed and report honest fallback provenance."""
    has_cjk = any("\u4e00" <= char <= "\u9fff" for char in text)
    first_loadable_fallback: dict | None = None
    for candidate in FONT_CANDIDATES:
        if not candidate or not Path(candidate).exists():
            continue
        try:
            font = ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
        likely_cjk = any(token in Path(candidate).name.lower() for token in CJK_FONT_NAME_TOKENS)
        info = {
            "font_path": candidate,
            "font_name": Path(candidate).name,
            "cjk_text": has_cjk,
            "supports_cjk": (not has_cjk) or likely_cjk,
            "warning": None if (not has_cjk or likely_cjk) else "Selected fallback font may not contain Chinese glyphs.",
            "font": font,
        }
        if not has_cjk or likely_cjk:
            return info
        if first_loadable_fallback is None:
            first_loadable_fallback = info
    if first_loadable_fallback is not None:
        return first_loadable_fallback
    return {
        "font_path": None,
        "font_name": "Pillow default bitmap font",
        "cjk_text": has_cjk,
        "supports_cjk": not has_cjk,
        "warning": "No configured font was loadable; Chinese glyphs may render as tofu." if has_cjk else None,
        "font": ImageFont.load_default(),
    }


def load_font(size: int, text: str = ""):
    return font_metadata(text=text, size=size)["font"]


def wrap_text(draw, text: str, font, max_width: int) -> list[str]:
    # Keep each CJK character independently wrappable while preserving Latin
    # words such as "Omega-3", "SCFA", or "and" as indivisible tokens.
    tokens = re.findall(r"[\u4e00-\u9fff]|[^\u4e00-\u9fff\s]+|\s+", text)
    lines: list[str] = []
    current = ""
    for token in tokens:
        if token.isspace():
            if current and not current.endswith(" "):
                current += " "
            continue
        candidate = current + token
        if draw.textbbox((0, 0), candidate.rstrip(), font=font)[2] <= max_width or not current.strip():
            current = candidate
        else:
            lines.append(current.rstrip())
            current = token.lstrip()
    if current.strip():
        lines.append(current.rstrip())
    return lines


def fit_text(draw, text: str, max_width: int, max_height: int, max_lines: int, start_size: int, min_size: int = 12):
    for size in range(start_size, min_size - 1, -2):
        font = load_font(size, text=text)
        lines = wrap_text(draw, text, font, max_width)
        line_height = max(1, size + 6)
        if len(lines) <= max_lines and line_height * len(lines) <= max_height:
            return font, lines, False
    font = load_font(min_size, text=text)
    lines = wrap_text(draw, text, font, max_width)[:max_lines]
    return font, lines, True
