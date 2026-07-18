from pathlib import Path

from PIL import Image, ImageDraw, ImageOps


def _panel(path: Path | None, label: str, size: tuple[int, int]) -> Image.Image:
    canvas = Image.new("RGB", size, "#FFF8EC")
    draw = ImageDraw.Draw(canvas)
    if path and path.exists():
        with Image.open(path).convert("RGB") as source:
            fitted = ImageOps.contain(source, (size[0] - 24, size[1] - 64))
            canvas.paste(fitted, ((size[0] - fitted.width) // 2, 48))
    else:
        draw.rounded_rectangle((24, 80, size[0] - 24, size[1] - 24), radius=18, fill="#CFE8F5", outline="#DCCDEE", width=3)
        draw.text((size[0] // 2 - 100, size[1] // 2), "NOT AVAILABLE", fill="#315B61")
    draw.text((24, 18), label, fill="#315B61")
    return canvas


def create_comparison_contact_sheet(out: str | Path) -> Path:
    out = Path(out)
    panel_size = (420, 560)
    panels = [
        _panel(out / "layout_mock_preview.png", "1  LAYOUT MOCK", panel_size),
        _panel(out / "illustration_raw.png", "2  RAW GENERATED ARTWORK", panel_size),
        _panel(out / "illustration_final.png", "3  FINAL OVERLAID POSTER", panel_size),
    ]
    sheet = Image.new("RGB", (panel_size[0] * 3, panel_size[1]), "#CFE8F5")
    for index, panel in enumerate(panels):
        sheet.paste(panel, (index * panel_size[0], 0))
    destination = out / "comparison_contact_sheet.png"
    sheet.save(destination, format="PNG")
    return destination
