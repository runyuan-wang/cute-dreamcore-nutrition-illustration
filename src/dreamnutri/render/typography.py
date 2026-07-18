import os
from pathlib import Path

from PIL import ImageFont


FONT_CANDIDATES = [
    os.getenv("DREAMNUTRI_FONT_PATH", ""),
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/System/Library/Fonts/Supplemental/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in FONT_CANDIDATES:
        if candidate and Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def wrap_text(draw, text: str, font, max_width: int) -> list[str]:
    cjk = any("\u4e00" <= char <= "\u9fff" for char in text)
    words = list(text) if cjk else text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = current + word if cjk else (f"{current} {word}" if current else word)
        if not cjk and current:
            candidate = f"{current} {word}"
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def fit_text(draw, text: str, max_width: int, max_height: int, max_lines: int, start_size: int, min_size: int = 12):
    for size in range(start_size, min_size - 1, -2):
        font = load_font(size)
        lines = wrap_text(draw, text, font, max_width)
        line_height = max(1, size + 6)
        if len(lines) <= max_lines and line_height * len(lines) <= max_height:
            return font, lines, False
    font = load_font(min_size)
    lines = wrap_text(draw, text, font, max_width)[:max_lines]
    return font, lines, True
