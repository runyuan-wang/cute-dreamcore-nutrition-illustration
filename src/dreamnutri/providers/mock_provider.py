import random
from pathlib import Path

from PIL import Image, ImageDraw

from dreamnutri.render.typography import load_font

from .base import MOCK_PREVIEW_LABEL, ImageProvider, ProviderResult


class MockProvider(ImageProvider):
    name = "mock"

    def generate(self, prompt: str, negative_prompt: str, width: int, height: int, output_path: Path, seed: int | None = None, model: str | None = None) -> ProviderResult:
        rng = random.Random(seed or 42)
        image = Image.new("RGB", (width, height), "#CFE8F5")
        draw = ImageDraw.Draw(image)
        colors = ["#FFF8EC", "#CDE8D1", "#F6B7A5", "#F8D98B", "#DCCDEE", "#AFCFE3"]
        draw.rectangle((0, 0, width, height), fill="#CFE8F5")
        for _ in range(16):
            x = rng.randint(-100, width + 100)
            y = rng.randint(0, height)
            r = rng.randint(30, 100)
            draw.ellipse((x - r, y - r // 2, x + r, y + r // 2), fill="#FFFDF8")
        hero = (width // 2, int(height * 0.56))
        draw.ellipse((hero[0] - width * 0.28, hero[1] - height * 0.07, hero[0] + width * 0.28, hero[1] + height * 0.07), fill="#7EBB91", outline="#315B61", width=4)
        draw.polygon([(hero[0] - width * 0.23, hero[1] + height * 0.05), (hero[0] + width * 0.22, hero[1] + height * 0.05), (hero[0] + width * 0.15, hero[1] + height * 0.16), (hero[0] - width * 0.17, hero[1] + height * 0.15)], fill="#CDE8D1")
        for index in range(6):
            x = int(width * (0.12 + index * 0.15))
            y = int(height * (0.25 + (index % 2) * 0.12))
            radius = int(min(width, height) * 0.055)
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=colors[index % len(colors)], outline="#315B61", width=3)
            draw.ellipse((x - radius // 3, y - radius // 5, x - radius // 7, y + radius // 8), fill="#FFFDF8")
            draw.ellipse((x + radius // 7, y - radius // 5, x + radius // 3, y + radius // 8), fill="#FFFDF8")
        for index in range(12):
            x = rng.randint(30, width - 30)
            y = rng.randint(int(height * 0.36), int(height * 0.82))
            draw.ellipse((x - 7, y - 7, x + 7, y + 7), fill="#F8D98B")
        draw.arc((hero[0] - width * 0.16, hero[1] - height * 0.04, hero[0] + width * 0.16, hero[1] + height * 0.07), 10, 170, fill="#315B61", width=4)
        banner_height = max(44, height // 22)
        draw.rectangle((0, 0, width, banner_height), fill="#EF8F7C")
        draw.text((18, max(8, banner_height // 5)), MOCK_PREVIEW_LABEL, font=load_font(max(18, width // 42)), fill="#FFFDF8")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path, format="PNG")
        return ProviderResult(raw_path=output_path, provider=self.name, requested_model=model, actual_model=None, response_id=None, seed=seed or 42, returned_dimensions=(width, height), metadata={"artwork_status": "mock_layout_only"})
