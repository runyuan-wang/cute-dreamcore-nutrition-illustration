"""Offline image provider that proves the real PNG decode/overlay path."""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

from PIL import Image

from .base import ImageProvider, ProviderResult


class FixtureImageProvider(ImageProvider):
    """Copy and decode a supplied PNG as a real-artwork test fixture.

    This is intentionally separate from ``MockProvider``: its output is allowed
    to become ``illustration_raw.png`` and receives honest fixture provenance.
    """

    name = "offline-png-fixture"

    def __init__(self, fixture_path: str | Path) -> None:
        self.fixture_path = Path(fixture_path)

    def generate(self, prompt, negative_prompt, width, height, output_path, seed=None, model=None):
        if not self.fixture_path.exists():
            raise FileNotFoundError(f"PNG fixture does not exist: {self.fixture_path}")
        try:
            with Image.open(self.fixture_path) as image:
                image.verify()
                dimensions = tuple(image.size)
        except Exception as exc:
            raise ValueError("PNG fixture could not be decoded and verified.") from exc
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(self.fixture_path, output_path)
        digest = hashlib.sha256(self.fixture_path.read_bytes()).hexdigest()
        return ProviderResult(
            raw_path=output_path,
            provider=self.name,
            requested_model=model or "offline-authentic-png-fixture",
            actual_model="offline-authentic-png-fixture",
            response_id=f"fixture-sha256:{digest}",
            seed=seed,
            returned_dimensions=dimensions,
            metadata={
                "execution": "offline_fixture",
                "fixture_sha256": digest,
                "fixture_path_name": self.fixture_path.name,
            },
        )
