from dataclasses import dataclass
from pathlib import Path


MOCK_PREVIEW_LABEL = "LAYOUT MOCK — NOT FINAL ARTWORK"


@dataclass
class ProviderResult:
    raw_path: Path
    provider: str
    requested_model: str | None
    actual_model: str | None = None
    response_id: str | None = None
    seed: int | None = None
    returned_dimensions: tuple[int, int] | None = None
    metadata: dict | None = None


class ProviderError(RuntimeError):
    """A provider could not return real artwork."""


class ImageProvider:
    name = "base"

    def generate(self, prompt: str, negative_prompt: str, width: int, height: int, output_path: Path, seed: int | None = None, model: str | None = None) -> ProviderResult:
        raise NotImplementedError
